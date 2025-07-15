import time
from pprint import pprint
import sys 
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from utils.llms import call_llm, call_local_llm ,get_model
from utils.utilities import escape_json
from utils.schemas.workflow import ArgoYAML
from .prompts import ZERO_SHOT_COT_SYSTEM_PROMPT, ZERO_SHOT_COT_USER_PROMPT
import time
import json
# from ruamel.yaml import YAML
# yaml = YAML()
import yaml
from io import StringIO

# Cloud
db_filepath = "./db/api_info/"
# LLM model name
# model_name = "gpt-4o"
# model_name = "ToolBench/ToolLLaMA-2-7b-v2"
model_name = "Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int8"
# Number of to feed into prompt
topk_nums = 10

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

def localmodel_generate_yaml_wf_from_query(query, model_name, model_instance,tokenizer, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            # Read the API information
            db_filename = db_filepath + 'api_information.json'
            api_info = read_json_to_dict(db_filename)
            # Find top-k functions
            topk_functions = find_topk_functions(query, api_info, topk_nums)
            topk_functions = json.dumps(topk_functions, indent=4)
            SYSTEM_PROMPT = ZERO_SHOT_COT_SYSTEM_PROMPT
            USER_PROMPT = ZERO_SHOT_COT_USER_PROMPT.format(query=query, topk_functions=topk_functions)
            # Call the local LLM
            print("Using Local Model")
            response = call_local_llm(
                _loaded_pipeline=model_instance,
                tokenizer=tokenizer,
                model_name=model_name,
                pydantic_schema=ArgoYAML,  # Pydantic schema for parsing
                schema_name="ArgoYAML",
                system_prompt=escape_json(SYSTEM_PROMPT),
                user_prompt=escape_json(USER_PROMPT)
            )
            try:
                response_yaml = response    
                yaml_buffer = StringIO()
                yaml.dump(response_yaml, yaml_buffer)
                yaml_string = yaml_buffer.getvalue()
                yaml_buffer.close()
                yaml_data = yaml.load(yaml_string, Loader=yaml.loader.Loader)
            except:
                print("--------Error in Parsing YAML file--------")
                continue
            return "Success", yaml_data
        
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            
            # Optional: Add a delay between retries
            time.sleep(1)  # 1-second delay before retrying
            
            # If the maximum attempts are reached, raise the error
            if attempt == max_retries:
                print("*"*50)
                return "Failed", response

def run_eval_opensource(model_name):
    """
    This function mimics the main() workflow but only processes `num_queries` queries per level 
    to allow quick testing on a small subset.
    """
    model_instance, tokenizer = get_model(model_name)
    start_time = time.time()
    # Directory mapping for levels
    levels = [
        "level1",
        "level2",
        "level3",
    ]

    # Process each level
    for level_name in levels:
        print(f"\n--- Testing {level_name}")
        results = []
        dir_path = "./eval/data/test_query"
        file_name = f"{level_name}_queries.json"
        input_file_path = os.path.join(dir_path, file_name)
        query_list = load_dataset(input_file_path)  
        for item in query_list:
            query = item["Query"]
            success_staus, argo_wf = localmodel_generate_yaml_wf_from_query(query, model_name, model_instance, tokenizer)
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
                json.dump(results, yaml_file, indent=2)
            print(f"{level_name} Generation Success")

        except Exception as e:
            print(f"Error saving file: {e} at {level_name}") 

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal testing execution time: {total_time:.2f} seconds")
    print("finished")

def main():
    model_name = "Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int8"
    run_eval_opensource(model_name)

if __name__ == "__main__":
    main()