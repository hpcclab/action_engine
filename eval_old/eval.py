import json

import openai
import sys
import os
from pathlib import Path

base_path = Path().resolve().parent
sys.path.append(str(base_path))



"""
func_selection accuracy 
Accuracy = Number of Correctly Selected Functions / Total Number of Ground Truth Function
"""

filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"
test_filename = filepath + 'eval_data/funcselection_test_1-2_nodes.json'
label_filename = filepath + 'answers/test_tasklist/tasklist_answer_1-2_nodes.json'
def read_json_to_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

test_data = read_json_to_dict(test_filename)
label_data = read_json_to_dict(label_filename)

accuracy_func_selector = [] 
for i in range(len(label_data)):
    correct_count = 0
    if test_data[i]["id"] == label_data[i]["id"]:
        label_api_names = [api["name"] for api in label_data[i]["selected_apis"]]
        test_api_names = [api["name"] for api in test_data[i]["api_names"]]
        for j in range(len(label_api_names)):
            if label_api_names[j] == test_api_names[j]:
                correct_count += 1
            # else: 
            #     correct_count -= 1
        acc_per_query = correct_count / len(label_api_names)
        accuracy_func_selector.append(acc_per_query)