import json
from ruamel.yaml import YAML
import sys
import os
import re

from pathlib import Path

base_path = Path().resolve().parent.parent.parent
sys.path.append(str(base_path))

from utils.subtask_div import subtask_diviser
from utils.func_identifier import func_identifier
from utils.wf_optimizer import wf_optimizer
from utils.data_dependency import confirm_dependency
from utils.argo_compiler import yaml_compiler
from utils.missing_func import missing_func
from utils.llm import call_llm, call_openai
from utils.utilities import escape_json
from utils.schemas.workflow import ArgoYAML

def read_json_to_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Get Test Data
filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/"
file_easy = filepath + 'answers/test_tasklist/tasklist_GTlabel_1-2_nodes.json'
file_inter = filepath + 'answers/test_tasklist/tasklist_GTlabel_3-5_nodes.json'
file_hard = filepath + 'answers/test_tasklist/tasklist_GTlabel_6-10_nodes.json'

test_easy = read_json_to_dict(file_easy)
test_inter = read_json_to_dict(file_inter)
test_hard = read_json_to_dict(file_hard)

#load faiss
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
loaded_faiss = FAISS.load_local(filepath + 'vectordb/LangChain_FAISS/', embedding_function, "api_vec", allow_dangerous_deserialization=True)

level = {
    "easy": test_easy,
    "inter" : test_inter,
    "hard": test_hard
}

#cloud
filepath = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/answers/test_endtoend/"
yaml = YAML()

def generate():
    # task_list = subtask_diviser(user_query)
    test = level[str(test_level)]
    user_query = test[i]["user_query"]
    task_list = test[i]["task_list"]
    selected_functions, no_func, non_func_list = func_identifier(task_list, user_query)
    

def action_engine(test_level, i):
    # task_list = subtask_diviser(user_query)
    test = level[str(test_level)]
    user_query = test[i]["user_query"]
    task_list = test[i]["task_list"]
    selected_functions, no_func, non_func_list = func_identifier(task_list, user_query)
    if not no_func:
        semantic_wf = wf_optimizer(user_query, task_list)
        selected_functions, user_inputs, dependent_params = confirm_dependency(semantic_wf, selected_functions)
        argo_wf = yaml_compiler(selected_functions, user_inputs)
    else:
        # print(non_func_list)
        message = missing_func(non_func_list)
        return message
    try:
        with open(filepath + f"action_engine/{test_level}/argo_workflow_{str(i+1)}.yaml", "w") as yaml_file:
            yaml.dump(argo_wf, yaml_file)

        """
        For testing purpose ease later
        """
        with open(filepath + "action_engine/test_details.json", 'w') as file:
            json.dump(selected_functions, file, indent=4) 
        # print(json.dumps(selected_functions, indent=4))
        return "Success"

    except Exception as e:
        with open(filepath + "action_engine/test_details.json", 'w') as file:
            json.dump(response, file, indent=4) 
        
        return f"Error saving file: {e}"
    return True


def ae_without_compiler(test_level, i):
    # task_list = subtask_diviser(user_query)
    test = level[str(test_level)]
    user_query = test[i]["user_query"]
    task_list = test[i]["task_list"]

    selected_functions, no_func, non_func_list = func_identifier(task_list, user_query)
    semantic_wf = wf_optimizer(user_query, task_list)
    selected_functions, user_inputs, dependent_params = confirm_dependency(semantic_wf, selected_functions)

    SYSTEM_PROMPT = '''
        You are the top-tier programmer.
        You will be given the information about dag. Each item inside the list represent one node including task description, function description. 
        Please construct Argo HTTP workflow with DAG templates. 
        The order of the list represents task order, please use name of the tasks as t plus index in the list like "t1", "t2", ..., "tn" where n as the last index of the list.

        You must generate the YAML content between the ```yaml and ``` tags.

        Here is the basic syntax for the Argo http template YAML file:

        apiVersion: argoproj.io/v1alpha1
        kind: Workflow
        metadata:
        generateName: http-wf-
        spec:
        arguments:
            parameters:
            - name: width
        entrypoint: main
        templates:
        - name: main
            inputs:
            parameters:
            - name: width
            dag:
            tasks:
            - name: t1
                template: tti-animation-art
                arguments:
                parameters:
                - name: prompt
                    value: '{{ tasks.t1.result }}'
                dependencies: []
            - name: t2
                template: tti-animation-art
                arguments:
                parameters:
                - name: prompt
                    value: '{{ tasks.t2.result }}'
                dependencies: []
        - name: tti-animation-art
            inputs:
            parameters:
            - name: prompt
            http:
            method: POST
            url:
            successCondition: response.statusCode == 200

        '''

    USER_PROMPT = f"""
            Information about dag: 
            {selected_functions}
        """
    response = call_openai(escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))

    # Use regular expression to extract the YAML content between the ```yaml and ``` tags
    yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)

        ##
    try:
        # Convert the extracted YAML string back to a Python dictionary to ensure it is valid YAML
            
        if yaml_match:
            argo_wf = yaml_match.group(1).strip()            

        argo_wf_dict = yaml.load(argo_wf)
        
        # Save it as a YAML file
        with open(filepath + f"ae_without_compiler/{test_level}/argo_workflow_{str(i+1)}.yaml", "w") as yaml_file:
            yaml.dump(argo_wf_dict, yaml_file)
        

        """
        For testing purpose ease later
        """
        with open(filepath + f"ae_without_compiler/details/{test_level}/test_details_{str(i+1)}.json", 'w') as file:
            json.dump(selected_functions, file, indent=4) 
             
        return "Success"

    except Exception as e:
        print("YAML content not found in the response.")
        try:
            print("Save sucess: at ", test_level, " Index:", i)
            print("*"*40)
            with open(filepath + f"ae_without_compiler/{test_level}/argo_workflow_{str(i+1)}.yaml", "w") as yaml_file:
                yaml.dump(response, yaml_file)
            """
            For testing purpose ease later
            """
            with open(filepath + f"ae_without_compiler/details/{test_level}/test_details_{str(i+1)}.json", 'w') as file:
                json.dump(selected_functions, file, indent=4) 
            
            return "Success"

        except Exception as e:
            """
            For testing purpose ease later
            """
            print("Save Failed")
            print("*"*40)
            with open(filepath + f"ae_without_compiler/details/{test_level}/test_details_{str(i+1)}.json", 'w') as file:
                json.dump(response, file, indent=4) 
            
            return f"Error saving file: {e}"

def ae_without_ddm_and_compiler(test_level, i):
    # task_list = subtask_diviser(user_query)
    test = level[str(test_level)]
    user_query = test[i]["user_query"]
    task_list = test[i]["task_list"]

    selected_functions, no_func, non_func_list = func_identifier(task_list, user_query)

    SYSTEM_PROMPT = '''
        You are the top-tier programmer.
        You will be given the information about dag. Each item inside the list represent one node including task description, function description. 
        Please construct Argo HTTP workflow with DAG templates. 
        The order of the list represents task order, please use name of the tasks as t plus index in the list like "t1", "t2", ..., "tn" where n as the last index of the list.

        You must generate the YAML content between the ```yaml and ``` tags.

        Here is the basic syntax for the Argo http template YAML file:

        apiVersion: argoproj.io/v1alpha1
        kind: Workflow
        metadata:
        generateName: http-wf-
        spec:
        arguments:
            parameters:
            - name: width
        entrypoint: main
        templates:
        - name: main
            inputs:
            parameters:
            - name: width
            dag:
            tasks:
            - name: t1
                template: tti-animation-art
                arguments:
                parameters:
                - name: prompt
                    value: '{{ tasks.t1.result }}'
                dependencies: []
            - name: t2
                template: tti-animation-art
                arguments:
                parameters:
                - name: prompt
                    value: '{{ tasks.t2.result }}'
                dependencies: []
        - name: tti-animation-art
            inputs:
            parameters:
            - name: prompt
            http:
            method: POST
            url:
            successCondition: response.statusCode == 200

        '''

    USER_PROMPT = f"""
            Information about dag: 
            {selected_functions}
        """
    response = call_openai(escape_json(SYSTEM_PROMPT), escape_json(USER_PROMPT))

    # Use regular expression to extract the YAML content between the ```yaml and ``` tags
    yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)

    try:
        if yaml_match:
            argo_wf = yaml_match.group(1).strip()            

        # Convert the extracted YAML string back to a Python dictionary to ensure it is valid YAML

        argo_wf_dict = yaml.load(argo_wf)
        
        # Save it as a YAML file
        with open(filepath + f"ae_without_dataflow_compiler/{test_level}/argo_workflow_{str(i+1)}.yaml", "w") as yaml_file:
            yaml.dump(argo_wf_dict, yaml_file)
        

        """
        For testing purpose ease later
        """
        with open(filepath + f"ae_without_dataflow_compiler/details/{test_level}/test_details_{str(i+1)}.json", 'w') as file:
            json.dump(selected_functions, file, indent=4) 
             
        return "Success"

    except Exception as e:
        print("YAML content not found in the response.")
        try:
            print("Save sucess: at ", test_level, " Index:", i)
            print("*"*40)
            with open(filepath + f"ae_without_dataflow_compiler/{test_level}/argo_workflow_{str(i+1)}.yaml", "w") as yaml_file:
                yaml.dump(response, yaml_file)
            """
            For testing purpose ease later
            """
            with open(filepath + f"ae_without_dataflow_compiler/details/{test_level}/test_details_{str(i+1)}.json", 'w') as file:
                json.dump(selected_functions, file, indent=4) 
            
            return "Success"

        except Exception as e:
            """
            For testing purpose ease later
            """
            print("Save Failed")
            print("*"*40)
            with open(filepath + f"ae_without_dataflow_compiler/details/{test_level}/test_details_{str(i+1)}.json", 'w') as file:
                json.dump(response, file, indent=4) 
            
            return f"Error saving file: {e}"


def main():
    res = []
    easy_res, inter_res, hard_res = [], [], []
    for i in range(len(test_easy)):
        try:
            easy_res.append(action_engine("easy", i))
            inter_res.append(action_engine("inter", i))
            hard_res.append(action_engine("hard", i))
        except Exception as e:
            print("*"*40)
            print("Feiled: ", i+1)
            hard_res.append(F"Failed:{e}")
            pass
    # hard_res.append(action_engine("hard", 3))

    ae_response = {"easy": easy_res, "inter": inter_res, "hard": hard_res}
    res.append({"ae" : ae_response})


    easy_res, inter_res, hard_res = [], [], []
    for i in range(len(test_inter)):
        try:
            easy_res.append(ae_without_compiler("easy", i))
            inter_res.append(ae_without_compiler("inter", i))
            hard_res.append(ae_without_compiler("hard", i))
        except Exception as e:
            print("*"*40)
            print("Feiled: ", i+1)
            hard_res.append(f"Failed: {e}")
            pass
    ae_wo_compiler_response = {"easy": easy_res, "inter": inter_res, "hard": hard_res}
    res.append({"ae_wo_compiler" : ae_wo_compiler_response})

    # easy_res, inter_res, hard_res = [], [], []
    # for i in range(len(test_hard)):
    #     try:
    #         easy_res.append(ae_without_ddm_and_compiler("easy", i))
    #         inter_res.append(ae_without_ddm_and_compiler("inter", i))
    #         hard_res.append(ae_without_ddm_and_compiler("hard", i))

    #     except Exception as e:
    #         print("*"*40)
    #         print("Feiled: ", i+1)
    #         hard_res.append(f"Failed: {e}")
    #         pass
    # ae_wo_dd_compiler_response = {"easy": easy_res, "inter": inter_res, "hard": hard_res}
    # res.append({"ae_wo_dd_compiler" : ae_wo_dd_compiler_response})
    return res
    
if __name__ == "__main__":
    print(main())


"""
First forget about different LLM
Now you need to program scoring.py
just only use [:1] in for loop to just test the script
once you finish generating scoring 
"""