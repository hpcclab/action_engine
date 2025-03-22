from pprint import pprint
import sys 
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from utils.llms import call_llm, get_model
from utils.utilities import escape_json
from utils.schemas.workflow import ArgoYAML
import time
import json
# from ruamel.yaml import YAML
# yaml = YAML()
import yaml
from io import StringIO

# Cloud
db_filepath = "./db/api_info/"
# LLM model name
model_name = "gpt-4o"
# Load the appropriate model
model_instance = get_model(model_name)

# Number of to feed into prompt
topk_nums = 30

from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
filepath = "./db/api_info/"
filename = filepath + 'api_information.json'
NO_FUNC = False

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = openai_api_key

embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
loaded_faiss = FAISS.load_local(db_filepath + 'vectordb/LangChain_FAISS/', embedding_function, "api_vec", allow_dangerous_deserialization=True)

def find_topk_functions(task: str, api_info, k):
    start=time.time()
    top_k = loaded_faiss.similarity_search_with_score(task, k)
    selected_id = [top_k[j][0].metadata["id"] for j in range(k)]
    topk_functions = [api_info[j-1] for j in selected_id]
    return topk_functions

def read_json_to_dict(filename):
    """
    Reads a JSON file that contains a single JSON array and returns it as a list of dictionaries.
    """
    with open(filename, 'r') as file:
        api_info = json.load(file)
    return api_info

def load_dataset(file_path):
    """
    Load the dataset from a JSON file.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_yaml_wf_from_query(query, model_name="gpt-4o", max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            # Read the API information
            db_filename = db_filepath + 'api_information.json'
            api_info = read_json_to_dict(db_filename)
            # Find top-k functions
            topk_functions = find_topk_functions(query, api_info, topk_nums)

            # System and user prompts
            SYSTEM_PROMPT = f'''
            Your task is to create Argo HTTP DAG workflows in YAML format based on user queries and available API information. 

            Follow these specific guidelines when generating the YAML file:
            1. For each parameter in the workflow:
            - If the parameter value is dependent on the result of another API, use the format: 
                `{{{{ tasks.<dependency API name>.result }}}}`.
                Example:
                ```yaml
                - name: weather
                value: '{{{{ tasks.checkweather.result }}}}'
                ```

            - If the parameter value is independent and comes from user input, use the format:
                `{{{{ inputs.parameters.<parameter name> }}}}`.
                Example:
                ```yaml
                - name: occasion
                value: '{{{{ inputs.parameters.occasion }}}}'
                ```

            2. Ensure the workflow is generated in a valid Argo YAML format without any additional text.
            '''


            USER_PROMPT = f"""
            User Query: {query}
            APIs: {topk_functions}
            Please generate the Argo HTTP DAG workflows in YAML format, let's think step by step:
            """
            
            # Call the LLM
            response = call_llm(
                model=model_instance,  # Pass the loaded model instance
                pydantic_schema=ArgoYAML,  # Pydantic schema for parsing
                schema_name="ArgoYAML",
                system_prompt=escape_json(SYSTEM_PROMPT),
                user_prompt=escape_json(USER_PROMPT)
            )
            response_yaml = response["extracted_yaml"]

            # Use StringIO to dump YAML to a string
            yaml_buffer = StringIO()
            yaml.dump(response_yaml, yaml_buffer)
            yaml_string = yaml_buffer.getvalue()
            yaml_buffer.close()

            yaml_data = yaml.load(yaml_string, Loader=yaml.loader.Loader)

            return "Success", yaml_data

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            
            # Optional: Add a delay between retries
            time.sleep(1)  # 1-second delay before retrying
            
            # If the maximum attempts are reached, raise the error
            if attempt == max_retries:
                print("*"*50)
                return "Failed", None

def main():
    # Directory mapping for levels
    levels = [
        "level1",
        "level2",
        "level3",
    ]

    # Process each level
    for level_name in levels:
        results = []
        dir_path = "./eval/data/test_query"
        file_name = f"{level_name}_queries.json"
        input_file_path = os.path.join(dir_path, file_name)
        query_list = load_dataset(input_file_path)
        for item in query_list:
            query = item["Query"]
            success_staus, argo_wf = generate_yaml_wf_from_query(query)
            generated_wf = {
                        "Id": item["Index"],
                        "status": success_staus, 
                        "workflow": argo_wf
                    }
            results.append(generated_wf)
        
        try:
            out_dir_path = "./eval/data/predict/LLMs/ZeroShot-CoT/" + model_name
            os.makedirs(out_dir_path, exist_ok=True)
            file_name = f"{level_name}_result.json"
            output_file_path = os.path.join(out_dir_path, file_name)
            with open(output_file_path, "w") as yaml_file:
                json.dump(results, yaml_file)
            print(f"{level_name} Generation Success")

        except Exception as e:
            print(f"Error saving file: {e} at {level_name}") 

if __name__ == "__main__":
    main()