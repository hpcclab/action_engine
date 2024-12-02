"""
This can use for assuming the all generation achives the success for Argo YAML generation.
Old_version of Scoring program
"""

import json

def read_json_to_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Load golden labels
# functions selection
filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"
function_filename_easy = filepath + 'answers/test_tasklist/tasklist_GTlabel_1-2_nodes.json'
function_filename_inter = filepath + 'answers/test_tasklist/tasklist_GTlabel_3-5_nodes.json'
function_filename_hard = filepath + 'answers/test_tasklist/tasklist_GTlabel_6-10_nodes.json'
function_label_easy = read_json_to_dict(function_filename_easy)
function_label_inter = read_json_to_dict(function_filename_inter)
function_label_hard = read_json_to_dict(function_filename_hard)

# topological ordering
filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"
ordering_filename_easy = filepath + 'answers/test_topologicalorder/topologicalorder_GTlabel_1-2_nodes.json'
ordering_filename_inter = filepath + 'answers/test_topologicalorder/topologicalorder_GTlabel_3-5_nodes.json'
ordering_filename_hard = filepath + 'answers/test_topologicalorder/topologicalorder_GTlabel_6-10_nodes.json'
ordering_label_easy = read_json_to_dict(ordering_filename_easy)
ordering_label_inter = read_json_to_dict(ordering_filename_inter)
ordering_label_hard = read_json_to_dict(ordering_filename_hard)

# data dependency 
filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"
dd_filename_easy = filepath + 'answers/test_datadependency/datadep_GTlabel_1-2_nodes.json'
dd_filename_inter = filepath + 'answers/test_datadependency/datadep_GTlabel_3-5_nodes.json'
dd_filename_hard = filepath + 'answers/test_datadependency/datadep_GTlabel_6-10_nodes.json'
dd_label_easy = read_json_to_dict(dd_filename_easy)
dd_label_inter = read_json_to_dict(dd_filename_inter)
dd_label_hard = read_json_to_dict(dd_filename_hard)

"""
func_selection accuracy 
Accuracy = Number of Correctly Selected Functions / Total Number of Ground Truth Function
"""
def acc_func_selector(dag, level, label_data):
    test_data = dag
    accuracy_func_selector = [] 
    syntax_error = False
    for j in range(len(label_data)):
        correct_count = 0
        if test_data[level][j]["id"] == label_data[j]["id"]:
            label_api_names = [api["name"] for api in label_data[j]["selected_apis"]]
            test_api_names = [api["name"] for api in test_data[level][j]["api_names"]]
            for k in range(len(label_api_names)):
                try:
                    if label_api_names[k].lower() == test_api_names[k].lower():
                        # print(label_api_names[k].lower(), " : ", test_api_names[k].lower())
                        correct_count += 1
                except:
                    syntax_error = True
            if syntax_error:
                 acc_per_query = 0
                 syntax_error = False
            else:
                acc_per_query = correct_count / len(label_api_names)
            accuracy_func_selector.append(acc_per_query)
    return accuracy_func_selector


"""
topologicl_order accuracy 
Accuracy  = Number of correctly ordered condition / Total number of condition
"""
def evaluate_accuracy(ground_truth, test_result):
    total_correct = 0
    total_pairs = 0
    additional_full_scores = 0  # Track the number of 0/0 cases

    # Iterate through both ground truth and test results
    for gt_item, test_item in zip(ground_truth, test_result):
        gt_pairs = set(gt_item['pairs'])  # Convert pairs to a set for easier comparison
        test_pairs = set(test_item['pairs'])
        
        if len(gt_pairs) == 0 and len(test_pairs) == 0:
            # Treat 0/0 as 100% correct
            additional_full_scores += 1
            # print(f"num {gt_item['num']}: 0 out of 0, counted as 100% correct")
        else:
            # Calculate the number of correctly ordered pairs
            correct_pairs = len(gt_pairs & test_pairs)  # Intersection of both sets
            total_correct += correct_pairs
            total_pairs += len(gt_pairs)
            # print(f"num {gt_item['num']}: {correct_pairs} out of {len(gt_pairs)} are correct")

    # Adjust the total correct to account for the 0/0 cases
    total_correct += additional_full_scores
    total_pairs += additional_full_scores

    # Calculate the accuracy
    accuracy = total_correct / total_pairs if total_pairs > 0 else 0

    return accuracy

def acc_topological_order(dag, level, label_set):
    test_set = dag[level]
    result_scores = []
    for i in range(len(test_set)):
        test_data = test_set[i]
        label_data = label_set[i]
        score = evaluate_accuracy(label_data['label'], test_data['topological_order'])
        result_scores.append(score)
    return result_scores


# Data Dependency Management
def generate_label_param_info(label_data):
    for i in range(len(label_data)):
        selected_apis = label_data[i]["selected_apis"]
        label_param_info = label_data[i]["param_dependency_management"]
        for j in range(len(label_param_info)):
            label_param_info[j]["dependent_params_with_source"] = selected_apis[j]["depended_params"]
    
    return label_data

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

def calculate_score_for_different_settings(dags):
    dag = dags
    res = {}
    for level in levels:
        # Func selection
        ae_dag_function_score = acc_func_selector(dag, level, labels[level]["func"])
        # Wf opt
        ae_dag_order_score = acc_topological_order(dag, level, labels[level]["order"])
        # Data dependency
        ae_dag_dd_score = acc_data_dependency(dag, level, labels[level]["dd"])
        # Maximum possible score for each index (since each component is out of 1, the max score is 3)
        max_score_per_index = 1
        # Calculate the total and normalize it to 100%
        ae_dag_function_score  = [round((sum(scores) / max_score_per_index) * 100, 1) for scores in zip(ae_dag_function_score)]
        ae_dag_order_score = [round((sum(scores) / max_score_per_index) * 100, 1) for scores in zip(ae_dag_order_score)]
        ae_dag_dd_score = [round((sum(scores) / max_score_per_index) * 100, 1) for scores in zip(ae_dag_dd_score)]
        max_score_per_index = 300
        normalized_total_scores = [round((sum(scores) / max_score_per_index) * 100, 1) for scores in zip(ae_dag_function_score, ae_dag_order_score, ae_dag_dd_score)]

        print(f"{level[0].upper()+level[1:]} Dataset scores (%):", normalized_total_scores)
        print("**Func Selection**")
        print(ae_dag_function_score)
        print("**wf_optimizer**")
        print(ae_dag_order_score)
        print("**dd**")
        print(ae_dag_dd_score)
        print()
        res[level] = {"total_score" : normalized_total_scores, "func_score": ae_dag_function_score, "topological_ordering": ae_dag_order_score, 'dd_score': ae_dag_dd_score}
        # res[level] = normalized_total_scores

    return res

#Evaluate
levels = ["easy", "inter", "hard"]
labels = {
    "easy": {"func": function_label_easy, "order": ordering_label_easy, "dd": dd_label_easy},
    "inter" : {"func": function_label_inter, "order": ordering_label_inter, "dd": dd_label_inter},
    "hard": {"func": function_label_hard, "order": ordering_label_hard, "dd": dd_label_hard}
}
result = {}
def run():


    # # load test data
    print("-"*40, "action_engine", "-"*40, )

    # """action_engine"""
    ae_filename = filepath + "answers/test_endtoend/action_engine/decomposed_dag.json"
    ae_dags = read_json_to_dict(ae_filename)
    dags = ae_dags[0]["action_engine"]
    result["ae"] = calculate_score_for_different_settings(dags)

    print("-"*40, "action_engine_without_compiler", "-"*40, )
    """action_engine_without_compiler"""
    ae_wo_compiler_filename = filepath + "answers/test_endtoend/ae_without_compiler/decomposed_dag.json"
    ae_wo_compiler_dags = read_json_to_dict(ae_wo_compiler_filename)
    dags = ae_wo_compiler_dags[0]["ae_without_compiler"]
    result["ae_wo_compiler"] = calculate_score_for_different_settings(dags)

    print("-"*40, "ae_wo_dd_compiler_filename", "-"*40, )
    """ae_wo_dd_compiler_filename"""
    ae_wo_dd_compiler_filename = filepath + "answers/test_endtoend/ae_without_dataflow_compiler/decomposed_dag.json"
    ae_wo_compiler_dags = read_json_to_dict(ae_wo_dd_compiler_filename)
    dags = ae_wo_compiler_dags[0]["ae_without_dataflow_compiler"]
    result["ae_wo_dd_compiler"] = calculate_score_for_different_settings(dags)


    with open(filepath + "answers/test_endtoend/result.json", "w") as f:
        json.dump(result, f, indent=4)

run()