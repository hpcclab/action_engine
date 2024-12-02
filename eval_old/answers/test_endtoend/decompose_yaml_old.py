import json
from ruamel.yaml import YAML
import re



def extract_task_number(s):
    match = re.search(r't\d+', s)
    return match.group(0) if match else None

def read_yaml(filepath):
    yaml = YAML()
    try:
        with open(filepath, "r") as yaml_file:
            data = yaml.load(yaml_file)
        return data
    except Exception as e:
        return f"Error reading file: {e}"
def hyphen_to_underscore(text):
    return text.replace('-', '_')

def decompose_yaml(filepath): 
    d = read_yaml(filepath)
    dag = d['spec']['templates'][0]['dag']['tasks']

    # selected function name
    api_names = []
    for i in range(len(dag)):
        api_names.append({"name": hyphen_to_underscore(dag[i]['template'])})
        # {"id": j+1,"api_names":[{"task_number": api["task_num"], "name": api["name"]} for api in selected_functions]}

    # topological order
    ## Divide YAML to topological order    
    dep_list, task_num, task_nums, topological_order, param_dependency_management  = [], [], [], [], []

    for item in dag:
        if "dependencies" in item and len(item["dependencies"]) != 0:
            dep_list.append(item["dependencies"])
    else: dep_list.append([])

    for i in range(len(dep_list)):
        if len(dep_list[i]) == 0 or (dep_list[i] == dep_list[i-1] and i > 0):
            pass
        else:
            task_nums.append(task_num)
            task_num = []
        task_num.append(i+1)
    task_nums.append(task_num)  

    for i in range(len(task_nums)):
        if len(task_nums[i]) > 1:
            topological = {
                "state": "paralell"
                }          
        else:
            topological = {
                "state": "sequential",
                } 

        topological["task_nums"]= [
                    i for i in task_nums[i]
                ]

        topological_order.append(topological)

    ## Create node pairs for evaluation purpose
    def generate_node_pairs(order_list):
        # Flatten the list_of_orders into a single list of numbers
        flattened_orders = [num for sublist in order_list for num in sublist]

        # Initialize the result list
        result = []

        # Generate the pairs for each number
        for j, current_num in enumerate(flattened_orders):
            pairs = []
            for k in range(j + 1, len(flattened_orders)):
                next_num = flattened_orders[k]
                pairs.append(f"{current_num} < {next_num}")
            
            # Add the result for the current number
            result.append({"num": current_num, "pairs": pairs})
        return result

    semantic_wf = topological_order
    # print("*"*40)
    # print(topological_order)
    order_list = [d["task_nums"] for d in semantic_wf] 
    pairs = generate_node_pairs(order_list)

#data depedency
    for i in range(len(dag)):
        user_input, dependent_paramas, dependent_params_with_source = [], [], []
        datadep = {
                "name": hyphen_to_underscore(dag[i]['template']),
                "all_params": [
                    item['name'] for item in dag[i]["arguments"]["parameters"]
                ]
            }
        for param in dag[i]["arguments"]["parameters"]:
            if "tasks" in str(param['value']):
                dependent_paramas.append(param['name'])
                dependent_params_with_source.append({str(param['name']): extract_task_number(param['value'])})
            else:
                user_input.append(param['name'])
        datadep["user_input"] = user_input
        datadep["dependent_params"] = dependent_paramas
        datadep["dependent_params_with_source"] = dependent_params_with_source
        param_dependency_management.append(datadep)

    dag_components = {"api_names": api_names, "topological_order": pairs, "param_dependency_management": param_dependency_management}
    return dag_components


def decompose(folder_name: str):
    levels = ['easy', 'inter', 'hard']
    easy, inter, hard = [], [], []
    for level in levels:
        for i in range(10):
            f_path =  f"/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/answers/test_endtoend/{folder_name}/{level}/argo_workflow_{str(i+1)}.yaml"
            dag = decompose_yaml(f_path)
            dag["id"] = i+1
            if level == "easy":
                easy.append(dag)
            elif level == "inter":
                inter.append(dag)
            else:
                hard.append(dag)
    result = {folder_name: {"easy": easy, "inter": inter, "hard": hard}}
    return result


def run():
    data = []
    ae_data = decompose("action_engine")
    data.append(ae_data)


    filenames = [{"path":"/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/answers/test_endtoend/action_engine/", "name": "action_engine"},
    {"path":"/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/answers/test_endtoend/ae_without_compiler/", "name": "ae_without_compiler"},
    {"path":"/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/answers/test_endtoend/ae_without_dataflow_compiler/", "name": "ae_without_dataflow_compiler"}]
    for file_path in filenames:
        data = []
        ae_data = decompose(file_path["name"])
        data.append(ae_data)
        filename = file_path["path"]
        with open(filename + "decomposed_dag.json", 'w') as f:
            json.dump(data, f, indent=4)


# data = []
# ae_data = decompose("ae_without_compiler")
# data.append(ae_data)
# filename = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/answers/test_endtoend/ae_without_compiler/"
# with open(filename + "decomposed_dag.json", 'w') as f:
#     json.dump(data, f, indent=4)

# data = []
# ae_data = decompose("ae_without_dataflow_compiler")
# data.append(ae_data)
# filename = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/answers/test_endtoend/ae_without_dataflow_compiler/"
# with open(filename + "decomposed_dag.json", 'w') as f:
#     json.dump(data, f, indent=4)