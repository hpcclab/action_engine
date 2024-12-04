"""
Identifying dependencies between functions
"""
from .llm import call_llm
from .schemas.workflow import TaskOutputDescription, DependentParams
from .utilities import escape_json

import json
import re

def semantic_wf_to_list(semantic_wf):
  """
  Extracting number and storing into the list
  Example
  input:
  semantic_wf = '''
    [Sequential State] - [1]  
    [Paralell State] - [2,3]  
    [Sequential State] - [4]
    '''
  output = [[1], [2,3], [4]]
  """
  pattern = r'\[(\d+(?:, ?\d+)*)\]'
  matches = re.findall(pattern, str(semantic_wf))
  # Convert the matched strings into lists of integers
  result = [[int(num) for num in match.split(',')] if ',' in match else [int(match)] for match in matches]
  
  return result

def generate_dependency_dict(list_of_dependencies):
    """
    Generating dependency dictionary
    Example
    Input: [[1], [2], [3]]
    output: {1: [], 2: [1], 3: [2]}
    """

    unique_numbers = set()  # To store all unique numbers
    dependency_dict = {}  # To store dependencies for each number
    for sublist in list_of_dependencies:
        unique_numbers.update(sublist)  # Update unique numbers set with elements from sublist
    for i, sublist in enumerate(list_of_dependencies[1:], start=1):  # Start from the second sublist
        for num in sublist:
            dependency_dict[num] = list_of_dependencies[i - 1]  # Set dependencies to the previous sublist
    for num in list_of_dependencies[0]: # Handle the first item in sublist
        dependency_dict[num] = []
    for num in unique_numbers: # Handle any numbers not found in subsequent sublists
        if num not in dependency_dict:
            dependency_dict[num] = []

    return dependency_dict

def form_output_description(selected_functions):
    SYSTEM_PROMPT = """
        You will be given a task, API functionality description, and API expected output description.
        The API is selected for the task, but the API output description is just for a general use case.
        Your job is to generate an API output description specialized in this given task.
        Do not make any assumptions; you must not make up any information.
        Generate the task-specific description ONLY from the given information.
        """

    for i in range(len(selected_functions)):
        USER_PROMPT = f"""
            Task Description: {selected_functions[i]["task_description"]},
            API Functionality Description: {selected_functions[i]["description"]}
            API Output Description: {selected_functions[i]["output_parameters_with_datatype"]}
            """
        response = call_llm(TaskOutputDescription, "TaskOutputDescription", escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))
        selected_functions[i]["output description"] = response["task_output_description"]
    data = {
            "sys_prompt": SYSTEM_PROMPT,
            "selected_functions": selected_functions
            }
    return selected_functions

def add_dependecy(semantic_wf, selected_functions):
    # generate_dependency_dict -> {1: [], 2: [1], 3: [2]}
    dependency_dict = generate_dependency_dict(semantic_wf_to_list(semantic_wf))
    # Adding dependency.

    for i in range(len(selected_functions)):
        selected_functions[i]["dependencies"] = [f"t{dp}" for dp in dependency_dict[i+1]]

    # generate output description
    selected_functions = form_output_description(selected_functions)

    # Dictionary to hold dependency output information
    dependency_output = {} 
    
    # Iterate over APIs to collect dependency output information
    for api in selected_functions: 
        dep_params_list = []
        dependency_outputs = {}
        for dependency in api['dependencies']:
            for dep_api in selected_functions:
                if f't{dep_api["task_num"]}' == dependency:
                    for param in dep_api["output_parameters_with_datatype"]:
                        dependency_outputs[dependency] = {
                            "output_data_type": param["datatype"],
                            "output_description": param["description"]
                        }
                        dep_params_list.append(dependency_outputs)
                    break
        api['dependency_output'] = dep_params_list

    return selected_functions


def list_to_dict_list(param_list:list) -> list:
    result_list = []
    for item in param_list:
        param_name = item.get('param_name')
        param_value = item.get('param_value')
        if param_name and param_value:  # Ensure both keys exist
            result_list.append({param_name: param_value})
    return result_list

def confirm_dependency(semantic_wf, selected_functions):
    selected_functions = add_dependecy(semantic_wf, selected_functions)

    for i in range(len(selected_functions)):
        param_list = []
        for p in selected_functions[i]["input_parameters_with_datatype"]:
            SYSTEM_PROMPT = f"""
                Objective:
                This task is to identify which past output parameters can be used as dependencies for the current parameter of an API call. The goal is to find dependencies by matching the current parameter’s data type and purpose with relevant outputs from past functions. **If there is no match in both data type and description, return an empty value for that parameter without selecting any past output.**

                Instruction:
                Current task number: t{i+1}
                Current parameter information: {p},
                Past output parameters: {[api["dependency_output"] for api in selected_functions[:i+1]]}

                You will receive:
                - The current parameter information, which includes the parameter name, expected data type, and description.
                - A list of past outputs from previous tasks, each containing an output data type, task number, and description.

                Task:
                1. Review the current parameter's data type and description and match it with past outputs based on two criteria: data type alignment and purpose/context alignment in descriptions.
                2. For each required parameter:
                - **Data Type Matching**: Only consider past outputs that have the same data type as the current parameter.
                - **Description Matching**: Evaluate whether the past output's description aligns with the purpose or context of the current parameter description.
                    - Consider an output relevant if its description indicates similar use or context to the current parameter.
                3. Select the most relevant past output if both criteria are met.
                - If multiple outputs are relevant, select the most recent one by task number.
                4. **If no past output matches both criteria (data type and description alignment), return an empty value for that parameter.**

                Example Matching Process:
                - If a required parameter has a type of `binary_image_file` and describes a need for an animated image, a past output with the same type and a similar description about an animated image would be considered a match.
                - If the required parameter specifies a type of `int` with a description about width, but no past outputs contain an integer type with a related purpose, it would be unmatched and should return an empty value for the parameter.

                Examples:
                OUTPUT EXAMPLE:
                {{
                    "DependentParams": [
                        {{
                            "param_name": "<name of the required parameter>",
                            "param_value": "<matching task number (e.g., t2) or empty if no match>"
                        }}
                    ]
                }}

                You must only generate the Answer. Your answer must be in JSON format. 
                Your Answer format must start with "```json" and end with "```".
                """
            USER_PROMPT = f"""
                Answer:
                """
            response = call_llm(DependentParams, "DependentParams", escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))
            # print("*"*40)
            a = [api["dependency_output"] for api in selected_functions[:i+1]]
            # print(f"Current params: {p}")
            # print(f"past params: {a}")
            # print(response)
            params = [param_list.append(i) for i in response["DependentParams"]]
        selected_functions[i]["depended_params"] = list_to_dict_list(param_list)
    # print(SYSTEM_PROMPT + USER_PROMPT)
    # print(response)
    # Get all input parameters names from all APIs
    all_input_params = [param for api in selected_functions for param in api['input_parameters_with_datatype']]
    # # Get depended parameters
    depended_params = set([list(param.keys())[0] for api in selected_functions for param in api['depended_params']])
    # # Collect input parameters except the depended ones
    user_inputs = [param for param in all_input_params if param["name"] not in depended_params]

    depended_params = list(depended_params)

    return selected_functions, user_inputs, depended_params
    
#user_inputs
#all
#depended

"""Original
[{'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}, {'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}]
[{'name': 'prompt', 'datatype': 'string'}, {'name': 'prompt', 'datatype': 'string'}, {'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}, {'name': 'file', 'datatype': 'binary_image_file'}, {'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}, {'name': 'file', 'datatype': 'binary_image_file'}]
{'file', 'prompt'}
"""

"""New
[{'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}, {'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}]
[{'name': 'prompt', 'datatype': 'string'}, {'name': 'prompt', 'datatype': 'string'}, {'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}, {'name': 'file', 'datatype': 'binary_image_file'}, {'name': 'width', 'datatype': 'int'}, {'name': 'height', 'datatype': 'int'}, {'name': 'file', 'datatype': 'binary_image_file'}]
{'prompt', 'file'}
"""