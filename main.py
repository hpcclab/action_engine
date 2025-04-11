from utils.subtask_div import subtask_diviser
from utils.func_identifier import func_identifier
from utils.wf_optimizer import wf_optimizer
from utils.data_dependency import confirm_dependency
from utils.argo_compiler import yaml_compiler
from utils.missing_func import missing_func
from utils.llms import get_model
import sys 
import json
from ruamel.yaml import YAML

#local
# filepath = "/home/UNT/ae0589/Desktop/HPCC/AutomaticWorkflowGeneration/ActionEngine/"
yaml = YAML()

#cloud
filepath = "./"

"""
Choose from below
"gpt-4o"
"gpt-3.5"
"meta-llama/Meta-Llama-3-8B-Instruct"
"mistralai/Mistral-7B-Instruct-v0.3"
"meta-llama/Llama-3.2-3B-Instruct"
"google/gemma-2b-it"
"""

model_name = "gpt-4o"
# user_query = "Create a graffiti-style image from a text prompt, enhance its quality, resize it to 800x600, convert it to a PDF, and send it via email."
user_query ="It will be perfect if you play music that matches my mood. This is Anna."
def main(user_query: str):
    model = get_model(model_name)
    task_list = subtask_diviser(model, user_query)
    selected_functions, NO_FUNC, non_func_list = func_identifier(model, task_list["Tasks"], user_query)
    semantic_wf = wf_optimizer(model, user_query, task_list)
    selected_functions, user_inputs, dependent_params = confirm_dependency(model, semantic_wf, selected_functions)
    argo_wf = yaml_compiler(selected_functions, user_inputs)

    ################
    # Only if you want to test the missing function function
    ################
    # if not no_func:
    #     semantic_wf = wf_optimizer(user_query, task_list)
    #     selected_functions, user_inputs, dependent_params = confirm_dependency(semantic_wf, selected_functions)
    #     print(json.dumps(selected_functions, indent=4))

    #     argo_wf = yaml_compiler(selected_functions, user_inputs)
    # else:
    #     message = missing_func(non_func_list)
    #     return message

    try:
        saved_path = filepath + "output_file/argo_workflow.yaml"
        with open(saved_path, "w") as yaml_file:
            yaml.dump(argo_wf, yaml_file)
            print("-"*50)
        return f"YAML Workflow is Successfully Saved at {saved_path}"
    except Exception as e:
        return f"Error saving file: {e}"
    return True

if __name__ == "__main__":   
    print(main(user_query))