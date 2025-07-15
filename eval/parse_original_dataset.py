"""

Generating YAML file from ReverseChain Dataset
Preprocess -> Removal of Data -> Generate YAML File

"""
import json
import os
import sys
import ast
import re
import random
from collections import Counter
from ruamel.yaml import YAML
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

file_path = "./eval/data/original_data.json"

def load_dataset(file_path):
    """
    Load the dataset from a JSON file.
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def add_api_name_list(data):
    # Getting a list of API names in order
    for i in range(len(data)):
    # for i in range(1):
        api_names_in_order = []
        for j in range(len(data[i]["APIs"])):
            try:
                api_name = data[i]["APIs"][j]["name"]
                if api_name in api_names_in_order:
                    print(data[i]["Index"])
                api_names_in_order.append(api_name)
            except:
                print(data[i]["Index"])
        data[i]["name_of_apis"] = api_names_in_order




def preprocess(data):
    def standardize_quotes(input_string):
        """Converts single quotes within arguments to double quotes."""
        input_string = re.sub(r"(?<=\w)'(?=\w|\s)", '"', input_string)  # Replace isolated single quotes within words
        input_string = re.sub(r"'([^']*)'", r'"\1"', input_string)  # Replace any string wrapped in single quotes with double quotes
        return input_string

    # AST Node Visitor class to find function calls followed by attribute access
    class DotAccessParser(ast.NodeVisitor):
        def __init__(self):
            self.api_with_dot_access = defaultdict(set)  # Store APIs with their dot-accessed attributes
            self.items_with_dot_access = set()  # Track data items with dot-accessed attributes

        def visit_Attribute(self, node):
            """Detect function calls followed by attribute access."""
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                api_name = node.value.func.id
                attribute_name = node.attr
                self.api_with_dot_access[api_name].add(attribute_name)  # Store the attribute
                self.items_with_dot_access.add(self.current_item_index)  # Track the item index
            self.generic_visit(node)

    # Initialize parser and counters
    parser = DotAccessParser()
    failed_indices = []
    delete_count = 0
    dot_access_count = 0
    total_items_checked = len(data)

    # Process each item in data
    for i, d in enumerate(data[:]):  # Iterate over a copy of the list to modify it safely
        parser.current_item_index = d["Index"]  # Set the current item's index for tracking
        function_call = standardize_quotes(d["Label"])
        try:
            # Attempt to parse the function call
            tree = ast.parse(function_call)
            parser.visit(tree)
        except SyntaxError:
            # Record the index and remove the item if there is a SyntaxError
            failed_indices.append(d["Index"])
            data.remove(d)
            delete_count += 1

    # Remove items with dot-accessed attributes
    for d in data[:]:  # Iterate over a copy again
        if d["Index"] in parser.items_with_dot_access:
            data.remove(d)
            dot_access_count += 1

    # Convert the result to the required format
    apis_with_dot_access = [
        {"name": api, "value": list(attributes)}
        for api, attributes in parser.api_with_dot_access.items()
    ]

    # Calculate remaining items
    remaining_items = total_items_checked - delete_count - dot_access_count

    # Output results
    print()
    print("-" * 40)
    print("APIs with dot-accessed outputs:", apis_with_dot_access)
    print("Total number of items checked:", total_items_checked)
    print("Number of items removed due to syntax errors:", delete_count)
    print("Number of items removed due to dot-access:", dot_access_count)
    print("Indices of removed items:", failed_indices)
    print("Number of items remaining:", remaining_items)


def level_division_by_node_numbers(data):
    # Initialize lists for each level
    level1 = []  # Items with 2 nodes
    level2 = []  # Items with 3 nodes
    level3 = []  # Items with 4 or 5 nodes

    # Populate the node count list and separate data into levels
    node_count = []
    for item in data:
        count = len(item["APIs"])  # Count the number of APIs
        node_count.append(count)  # Collect for summary statistics

        # Categorize items based on node count
        if count == 2:
            level1.append(item)
        elif count == 3:
            level2.append(item)
        elif count == 4 or count == 5:
            level3.append(item)

    # Ensure there are at least 150 items in each level for sampling
    level1_sample = random.sample(level1, min(100, len(level1)))  # Sample 150 or fewer if not enough items
    level2_sample = random.sample(level2, min(100, len(level2)))  
    level3_sample = random.sample(level3, min(100, len(level3)))  

    # Print counts for each level and the node distribution
    counts = Counter(node_count)
    print()
    print("-"*40)
    print("Node count distribution:", counts)
    print("Level 1 data (2 nodes):", len(level1))
    print("Level 2 data (3 nodes):", len(level2))
    print("Level 3 data (4 or 5 nodes):", len(level3))
    print("Sampled Level 1 (2 nodes):", len(level1_sample))
    print("Sampled Level 2 (3 nodes):", len(level2_sample))
    print("Sampled Level 3 (4 or 5 nodes):", len(level3_sample))
    return level1_sample, level2_sample, level3_sample


def yaml_generation(level1, level2, level3):
    class DependencyParser(ast.NodeVisitor):
        def __init__(self):
            self.dependencies = defaultdict(set)  # Store dependencies between functions
            self.parameters = defaultdict(dict)   # Store parameters for each function
            self.all_nodes = set()                # Track all API names
            self.current_parent = None

        def visit_Call(self, node):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name:
                self.all_nodes.add(func_name)  # Add the current function to the list of all nodes
                if self.current_parent:
                    self.dependencies[self.current_parent].add(func_name)  # Add a dependency for the parent function
                self.current_parent = func_name  # Update the current parent function

                # Parse the arguments
                for kw in node.keywords:
                    param_name = kw.arg
                    param_value = kw.value

                    # Check if the parameter is dependent on another function
                    if isinstance(param_value, ast.Call):
                        nested_func_name = param_value.func.id if isinstance(param_value.func, ast.Name) else None
                        if nested_func_name:
                            # Parameter depends on another function
                            self.parameters[func_name][param_name] = {
                                'name': param_name,
                                'value': f"{{{{ tasks.{nested_func_name.lower()}.result }}}}"
                            }
                            self.visit(param_value)  # Recursively visit the nested function
                    else:
                        # Parameter is a direct input
                        self.parameters[func_name][param_name] = {
                            'name': param_name,
                            'value': f"{{{{ inputs.parameters.{param_name} }}}}"
                        }

    # Initialize YAML handler
    yaml = YAML()
    yaml.default_flow_style = False

    # Directory mapping for levels
    level_directories = {
        "level1": level1,
        "level2": level2,
        "level3": level3
    }

    # Process each level
    total_result = []
    for level_name, level_data in level_directories.items():
        queries = []
        # Ensure the directory exists
        output_dir = "./eval/data/gt/"+level_name
        os.makedirs(output_dir, exist_ok=True)
        level_results = []
        # Process each item in the level
        for item in level_data:
            label = item["Label"]
            index = item["Index"]
            query = item["Query"]
            queries.append({"Index":index, "Query":query})
            
            # Generate function call and parse
            function_call = label
            parser = DependencyParser()
            try:
                tree = ast.parse(function_call)
                parser.visit(tree)
                
                # Generate tasks based on dependencies and parameters
                tasks = []
                for node in parser.all_nodes:  # Loop through all API nodes
                    dependencies = parser.dependencies[node]
                    task = {
                        'name': node.lower(),
                        'template': node.lower(),
                    }
                    if dependencies:
                        task['dependencies'] = [dep.lower() for dep in dependencies]  # Add dependencies if present
                    
                    # Add parameters for the task
                    task['arguments'] = {
                        'parameters': list(parser.parameters[node].values())  # Include all parameters
                    }
                    tasks.append(task)

                
                # Create the YAML structure
                argo_template = {
                    'apiVersion': 'argoproj.io/v1alpha1',
                    'kind': 'Workflow',
                    'metadata': {
                        'generateName': f'dependency-workflow-{index}-'
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

                # Save the YAML file
                file_name = f"test_yaml_{index}.yaml"
                file_path = os.path.join(output_dir, file_name)

                generated_wf = {
                            "Id": index,
                            "workflow": argo_template
                        }
                level_results.append(generated_wf)

                with open(file_path, 'w') as file:
                    file.write(f"# index: {index}\n")
                    file.write(f"# query: {query}\n\n")
                    yaml.dump(argo_template, file)

            except SyntaxError as e:
                print(f"Syntax error in function call for item at {level_name}[{index}] - {label}")
                print(e)
        total_result.append({str(f"{level_name}"):level_results})
        # save ground truth


        # save test query
        os.makedirs("./eval/data/test_query/", exist_ok=True)
        file_name = f"{level_name}_queries.json"
        file_path = os.path.join("./eval/data/test_query/", file_name)
        with open(file_path, 'w') as file:
            json.dump(queries, file)

    file_name = f"results.json"
    file_path = os.path.join("./eval/data/gt/", file_name)
    with open(file_path, 'w') as file:
        json.dump(total_result, file)

def main():
    # data = load_dataset(file_path)
    # add_api_name_list(data)
    # preprocess(data)
    # level1, level2, level3 = level_division_by_node_numbers(data)
    file_path = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/eval/data/test_query/levels_data.json"
    data = load_dataset(file_path)
    level1 = data[0]["level1"]
    level2 = data[1]["level2"]
    level3 = data[2]["level3"]
    yaml_generation(level1, level2, level3)

main()