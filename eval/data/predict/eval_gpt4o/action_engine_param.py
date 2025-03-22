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
from utils.missing_func import missing_func
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
    
def extract_subtasks(data):
    """
    Extract subtasks from the given dictionary and return as a list of dictionaries.
    
    :param data: Dictionary containing task information.
    :return: List of dictionaries with subtask numbers and descriptions.
    """
    return [
        {
            "subtask_number": function["task_num"],
            "subtask_description": function["task_description"]
        }
        for function in data.get("Selected_Functions", [])
    ]


def generate_yaml_file_from_query(user_query: str, selected_f,  max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            # Model setup and task division
            model = get_model(model_name)
            # task_list = subtask_diviser(model, user_query)
            # selected_functions, NO_FUNC, non_func_list = func_identifier(model, task_list["Tasks"], user_query)
            task_list = extract_subtasks(selected_f)
            selected_functions = selected_f["Selected_Functions"]
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

error_log_file = "/home/UNT/ae0589/project/action_engine/eval/data/predict/error_log.txt"
# Function to log errors
def log_error(log_file, message):
    with open(log_file, "a") as f:
        f.write(message + "\n")

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
        selected_funcs = load_dataset(f"/home/UNT/ae0589/project/action_engine/eval/data/test_query/param_evaluation/result_{level_name}.json")
        selected_funcs = sorted(selected_funcs, key=lambda x: x['Id'])
        query_list = load_dataset(input_file_path)
        query_list = sorted(query_list, key=lambda x: x['Index'])
        for i in range(len(query_list)):
            if query_list[i]["Index"] == selected_funcs[i]["Id"]:
                print(f"Running {level_name} at number {i}")
                query = query_list[i]["Query"]
                selected_f = selected_funcs[i]
                success_staus, argo_wf = generate_yaml_file_from_query(query, selected_f)
                if success_staus == "Failed":
                    print(f"Failed level: {level_name} at {query_list[i]["Index"]}")
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