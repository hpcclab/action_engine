import json
from ruamel.yaml import YAML
yaml = YAML()

import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from utils.subtask_div import subtask_diviser
from utils.func_identifier import func_identifier
from utils.wf_optimizer import wf_optimizer
from utils.data_dependency import confirm_dependency
from utils.argo_compiler import yaml_compiler
from utils.llms import get_model
#cloud
filepath = "./"

"""
Choose from below
"gpt-4o"
"gpt-3.5-turbo"
"meta-llama/Meta-Llama-3-8B-Instruct"
"mistralai/Mistral-7B-Instruct-v0.3"
"meta-llama/Llama-3.2-3B-Instruct"
"google/gemma-2b-it"
"""
model_name = "gpt-4o"

import time  # Optional: for adding a delay between retries

def load_dataset(file_path):
    """
    Load the dataset from a JSON file.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_yaml_file_from_query(user_query: str, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            # Model setup and task division
            model = get_model(model_name)
            task_list = subtask_diviser(model, user_query)
            selected_functions, NO_FUNC, non_func_list = func_identifier(model, task_list["Tasks"], user_query)
            semantic_wf = wf_optimizer(model, user_query, task_list)
            selected_functions, user_inputs, dependent_params = confirm_dependency(model, semantic_wf, selected_functions)
            
            # Workflow compilation
            argo_wf = yaml_compiler(selected_functions, user_inputs)
            
            # If everything succeeds, return success
            return "Success", argo_wf
        
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
            success_staus, argo_wf = generate_yaml_file_from_query(query)
            generated_wf = {
                        "Id": item["Index"],
                        "status": success_staus, 
                        "workflow": argo_wf
                    }
            results.append(generated_wf)
        
        try:
            out_dir_path = "./eval/data/predict/AE/" + model_name
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