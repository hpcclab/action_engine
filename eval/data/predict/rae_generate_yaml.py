import json

import ast
from collections import defaultdict
import sys 
import os
from ruamel.yaml import YAML
yaml = YAML()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from actione_engine_reverse.main_rae import ReverseActionEngine
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

from collections import defaultdict
import ast

class DependencyParser(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = defaultdict(set)  # Using set for unique dependencies
        self.parameters = defaultdict(dict)   # Using dict for unique parameters per name
        self.current_parent = None

    def visit_Call(self, node):
        func_name = node.func.id if isinstance(node.func, ast.Name) else None
        if func_name:
            if self.current_parent:
                # Record function dependency if it's not already added
                self.dependencies[self.current_parent].add(func_name)
            self.current_parent = func_name
            
            # Handle arguments and differentiate dependencies
            for kw in node.keywords:
                param_name = kw.arg
                param_value = kw.value

                # Check if the parameter is a nested function (indicating dependency)
                if isinstance(param_value, ast.Call):
                    nested_func_name = param_value.func.id if isinstance(param_value.func, ast.Name) else None
                    if nested_func_name:
                        # Add dependent parameter
                        self.parameters[func_name][param_name] = {
                            'name': param_name,
                            'value': f"{{{{ tasks.{nested_func_name.lower()}.result }}}}"
                        }
                        self.visit(param_value)  # Recursive call to check further nesting
                else:
                    # Add parameter as user input
                    self.parameters[func_name][param_name] = {
                        'name': param_name,
                        'value': f"{{{{ inputs.parameters.{param_name} }}}}"
                    }

def load_dataset(file_path):
    """
    Load the dataset from a JSON file.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

import ast

def function_call_to_yaml(parser, function_call: str):
    try:
        # Parse the function call into an AST
        tree = ast.parse(function_call, mode='eval')  # Use 'eval' mode for expressions
        parser.visit(tree)  # Populate parser dependencies and parameters
        
        # Debug: Check parser output
        print("Dependencies:", parser.dependencies)
        print("Parameters:", parser.parameters)

        # Generate tasks based on dependencies and parameters
        tasks = []
        for node in reversed(parser.dependencies):  # Reverse the order of nodes
            dependencies = parser.dependencies[node]
            task = {
                'name': node.lower(),
                'template': node.lower(),
            }
            if dependencies:
                task['dependencies'] = [dep.lower() for dep in dependencies]  # Convert each dependency to lowercase
            
            # Add parameters to each task
            task['arguments'] = {
                'parameters': list(parser.parameters[node].values())  # Use unique parameters only
            }
            tasks.append(task)
        
        # Create the YAML structure
        argo_template = {
            'apiVersion': 'argoproj.io/v1alpha1',
            'kind': 'Workflow',
            'metadata': {
                'generateName': f'dependency-workflow'
            },
            'spec': {
                'entrypoint': 'main',
                'templates': [
                    {
                        'name': 'main',
                        'dag': {
                            'tasks': tasks
                        }
                    }
                ]
            }
        }
        return "Success", argo_template
    
    except Exception as e:
        # Debug: Catch and log exceptions
        print("Error during YAML conversion:", str(e))
        return "Failed", None

        
def main():
    model = get_model(model_name)
    parser = DependencyParser()
    ReverseAE = ReverseActionEngine(model)

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
        query_list = load_dataset(input_file_path)
        count = 0
        for item in query_list:
            query = item["Query"]
            print(f"Index: {item["Index"]}. Processing query: {query}")
            result_in_function_call_format = ReverseAE.reverse_action_engine(query)
            print("^"*30)
            print(f"Function call format generated: {result_in_function_call_format}")
            print("^"*30)
            success_staus, argo_wf = function_call_to_yaml(parser, result_in_function_call_format)
            # print(f"YAML conversion result: {success_staus}")
            generated_wf = {
                        "Id": item["Index"],
                        "status": success_staus, 
                        "workflow": argo_wf
                    }
            results.append(generated_wf)
            count+=1
            print("Finished at query #", count)

        try:
            out_dir_path = "./eval/data/predict/AE_Reverse/" + model_name
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
    # from pprint import pprint
    # parser = DependencyParser()
    # result_in_function_call_format = "AddSongToPlaylist(user_ID=GetUserIDByUser(user_name='Emma'), playlist_ID='Classic Disco Hits', song_name='Hey Jude')"
    # success_staus, argo_wf = function_call_to_yaml(parser, result_in_function_call_format)
    # print(f"YAML conversion result: {success_staus}")
    # pprint(argo_wf)
    # Choose a model for testing
    # model = get_model(model_name)
    # # Initialize the ReverseActionEngine with the selected model
    # reverse_engine = ReverseActionEngine(model)
    # # Provide a test user request
    # user_request = "I need the current weather in New York and a 3-day forecast."

    # # Call the reverse_action_engine method with the test request
    # try:
    #     workflow = reverse_engine.reverse_action_engine(user_request)
    #     print("Generated Workflow:")
    #     print(workflow)
    # except Exception as e:
    #     print(f"An error occurred during workflow generation: {e}")