import json

import openai
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.func_identifier import func_identifier

filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"
filename = filepath + 'answers/test_tasklist/tasklist_answer_1-2_nodes.json'

def read_json_to_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


test_data = read_json_to_dict(filename)

selected_func = []
for i in range(len(test_data)):
    selected_functions, no_func, non_func_list = func_identifier(test_data[i]["task_list"], test_data[i]["user_query"])
    selected_func.append({"id": i+1, "api_names":[{"task_number": api["task_num"], "name": api["name"]} for api in selected_functions]})

with open(filepath + 'eval_data/funcselection_test_1-2_nodes.json', 'w') as json_file:
    json.dump(selected_func, json_file, indent=4)