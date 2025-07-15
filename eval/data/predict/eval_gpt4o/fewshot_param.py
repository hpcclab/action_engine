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
model_instance, _ = get_model(model_name)

# Number of to feed into prompt
topk_nums = 20

from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

NO_FUNC = False

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = openai_api_key



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

def generate_yaml_wf_from_query(query, selected_functions, model_name="gpt-4o", max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            selected_functions = selected_functions["Selected_Functions"]
            topk_functions = []
            for f in selected_functions:
                filtered_func = {key: value for key, value in f.items() if key not in ['task_num', 'task_description']}
                topk_functions.append(filtered_func)
            
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
            
            Here are some examples of queries and the corresponding workflows:

            Example 1:
            User Query: 'sarah_wilson' wants to reserve the book 'Moby-Dick'. Start from September 12th to September 26th.
            Output:
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
            generateName: dependency-workflow-22-
            spec:
            entrypoint: main
            templates:
            - name: main
                dag:
                tasks:
                - name: username2email
                    template: username2email
                    dependencies:
                    - title2isbn
                    arguments:
                    parameters:
                    - name: username
                        value: '{{ inputs.parameters.username }}'
                - name: title2isbn
                    template: title2isbn
                    arguments:
                    parameters:
                    - name: title
                        value: '{{ inputs.parameters.title }}'
                - name: reservebook
                    template: reservebook
                    dependencies:
                    - username2email
                    arguments:
                    parameters:
                    - name: user_email
                        value: '{{ tasks.username2email.result }}'
                    - name: ISBN
                        value: '{{ tasks.title2isbn.result }}'
                    - name: start_date
                        value: '{{ inputs.parameters.start_date }}'
                    - name: end_date
                        value: '{{ inputs.parameters.end_date }}'


            Example 2:
            User Query: Can you book a flight from my city to New York on May 15th?
            Output:
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
            generateName: dependency-workflow-1542-
            spec:
            entrypoint: main
            templates:
            - name: main
                dag:
                tasks:
                - name: findflight
                    template: findflight
                    dependencies:
                    - fetchcity
                    arguments:
                    parameters:
                    - name: cityDeparture
                        value: '{{ tasks.fetchcity.result }}'
                    - name: cityArrival
                        value: '{{ inputs.parameters.cityArrival }}'
                    - name: date
                        value: '{{ inputs.parameters.date }}'
                - name: bookflight
                    template: bookflight
                    dependencies:
                    - fetchflightid
                    arguments:
                    parameters:
                    - name: flight_ID
                        value: '{{ tasks.fetchflightid.result }}'
                    - name: date
                        value: '{{ inputs.parameters.date }}'
                - name: getuserid
                    template: getuserid
                    arguments:
                    parameters:
                    - name: username
                        value: '{{ inputs.parameters.username }}'
                - name: fetchflightid
                    template: fetchflightid
                    dependencies:
                    - findflight
                    arguments:
                    parameters:
                    - name: flight_name
                        value: '{{ tasks.findflight.result }}'
                - name: fetchcity
                    template: fetchcity
                    dependencies:
                    - getuserid
                    arguments:
                    parameters:
                    - name: user_ID
                        value: '{{ tasks.getuserid.result }}'
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
            
error_log_file = "/home/UNT/ae0589/project/action_engine/eval/data/predict/error_log.txt"
# Function to log errors
def log_error(log_file, message):
    with open(log_file, "a") as f:
        f.write(message + "\n")

def main():
    start_time = time.time()
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
        selected_funcs = load_dataset(f"/home/UNT/ae0589/project/action_engine/eval/data/test_query/param_evaluation/result_{level_name}.json")
        selected_funcs = sorted(selected_funcs, key=lambda x: x['Id'])
        query_list = load_dataset(input_file_path)
        query_list = sorted(query_list, key=lambda x: x['Index'])
        for i in range(len(query_list)):
            if query_list[i]["Index"] == selected_funcs[i]["Id"]:
                print(f"Running {level_name} at number {i}")
                query = query_list[i]["Query"]
                selected_f = selected_funcs[i]
                success_staus, argo_wf = generate_yaml_wf_from_query(query, selected_f)
                generated_wf = {
                            "Id": query_list[i]["Index"],
                            "status": success_staus, 
                            "workflow": argo_wf
                        }
                results.append(generated_wf)

            else:
                error_message = f"Id does not match at Qery:{query_list[i]["Query"]}, Func:{selected_funcs[i]["Id"]}"
                print(error_message)
                log_error(error_log_file, error_message)
        
        try:
            out_dir_path = "./eval/data/predict/LLMs/FewShot/" + model_name
            os.makedirs(out_dir_path, exist_ok=True)
            file_name = f"{level_name}_result.json"
            output_file_path = os.path.join(out_dir_path, file_name)
            with open(output_file_path, "w") as yaml_file:
                json.dump(results, yaml_file)
            print(f"{level_name} Generation Success")

        except Exception as e:
            print(f"Error saving file: {e} at {level_name}") 

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()