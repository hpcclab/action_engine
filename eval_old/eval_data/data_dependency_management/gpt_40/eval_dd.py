import json

import openai
import sys
import os
from pathlib import Path

filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"

def read_json_to_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Read dd lables
dd_filename_easy = filepath + 'answers/test_datadependency/datadep_GTlabel_1-2_nodes.json'
dd_filename_inter = filepath + 'answers/test_datadependency/datadep_GTlabel_3-5_nodes.json'
dd_filename_hard = filepath + 'answers/test_datadependency/datadep_GTlabel_6-10_nodes.json'
dd_label_easy = read_json_to_dict(dd_filename_easy)
dd_label_inter = read_json_to_dict(dd_filename_inter)
dd_label_hard = read_json_to_dict(dd_filename_hard)

# Read test data
dd_test_filename_easy = filepath + 'eval_data/data_dependency_management/gpt_40/easy_1-2_nodes.json'
dd_test_filename_inter = filepath + 'eval_data/data_dependency_management/gpt_40/inter_3-5_nodes.json'
dd_test_filename_hard = filepath + 'eval_data/data_dependency_management/gpt_40/hard_6-10_nodes.json'
dd_test_easy = read_json_to_dict(dd_test_filename_easy)
dd_test_inter = read_json_to_dict(dd_test_filename_inter)
dd_test_hard = read_json_to_dict(dd_test_filename_hard)



datadependency_result={}

"""
Metrices:
Correct Dependency Accuracy =  Number of Correctly Identified Dependencies / Total Number of Dependencies in Ground Truth

"""

def acc_data_dependency(dag, level, label_set):
    label_data = generate_label_param_info(label_set)
    scores = []
    #for each query
    for i in range(len(dag[level])):
        correct_params, total_params = 0, 0
        test_param_info = dag[level][i]["param_dependency_management"]
        label_param_info = label_data[i]["param_dependency_management"]
        # for each function   
        for j in range(len(test_param_info)):
            if test_param_info[j]["name"].lower() == label_param_info[j]["name"].lower():
                test = test_param_info[j]
                gt = label_param_info[j]
                if len(test_param_info[j]["all_params"]) == 0:
                    # if system was not able to extract parameter, count as 0 accuracy
                    pass
                else: 
                    test_user_input = set(test['user_input'])
                    gt_user_input = set(gt['user_input'])
                    test_dependent_params = set(test['dependent_params'])
                    gt_dependent_params = set(gt['dependent_params'])

                    # user input params
                    correct_user_input = len(gt_user_input & test_user_input) 
                    total_user_input = len(gt_user_input)
                    # dependent params
                    common_params = list(gt_dependent_params & test_dependent_params)
                    if common_params:
                        common_dicts = [item for item in test["dependent_params_with_source"] if item in gt["dependent_params_with_source"]]
                        correct_dependent_params = len(common_dicts)
                    else:    
                        correct_dependent_params = 0
                    total_dependent_params = len(gt_dependent_params)
                    
                    correct_params += (correct_user_input + correct_dependent_params)
                    total_params += (total_user_input + total_dependent_params)
            else: 
                pass # exclude if the wrong function were selected
        if correct_params != 0:        
            per_query_acc = correct_params / total_params
        else: per_query_acc = 0
        scores.append(per_query_acc)
    return scores


levels = ["easy", "inter", "hard"]
labels = {
    "easy": {"func": function_label_easy, "order": ordering_label_easy, "dd": dd_label_easy},
    "inter" : {"func": function_label_inter, "order": ordering_label_inter, "dd": dd_label_inter},
    "hard": {"func": function_label_hard, "order": ordering_label_hard, "dd": dd_label_hard}
}
result = {}
dags = dd_test_easy[0]["action_engine"]
result["ae"] = calculate_score_for_different_settings(dags)