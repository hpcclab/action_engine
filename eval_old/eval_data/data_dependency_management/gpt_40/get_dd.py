import json

def read_json_to_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"
ae_filename = filepath + "answers/test_endtoend/action_engine/decomposed_dag.json"
levels = ["easy", "inter", "hard"]
ae_dags = read_json_to_dict(ae_filename)
dag = ae_dags[0]["action_engine"]["easy"]


for level in levels:
    dag = ae_dags[0]["action_engine"][level]
    data_list = []
    for i in range(len(dag)):
        data = {"id": dag[i]["id"], "selected_apis": dag[i]["api_names"], "param_dependency_management": dag[i]["param_dependency_management"]}
        data_list.append(data)
    if level =="easy":
        with open(filepath + "eval_data/data_dependency_management/gpt_40/easy_1-2_nodes.json", 'w') as file:
            json.dump(data_list, file, indent=4)
            print("successfully save in level: ", level)
    elif level =="inter":
        with open(filepath + "eval_data/data_dependency_management/gpt_40/inter_3-5_nodes.json", 'w') as file:
            json.dump(data_list, file, indent=4)
            print("successfully save in level: ", level)
    elif level =="hard":
        with open(filepath + "eval_data/data_dependency_management/gpt_40/hard_6-10_nodes.json", 'w') as file:
            json.dump(data_list, file, indent=4)
            print("successfully save in level: ", level)