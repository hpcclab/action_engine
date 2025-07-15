import os
import yaml
import json

def generate_ground_truth(yaml_file_path, unique_id):
    """
    Generate the ground truth data from a YAML file.
    Adds the unique Id to the result.
    """
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Initialize the structure for gold_data
    gold_data = {"Id": unique_id, "gold_data": {"conversations": [{"value": ""}]}}
    api_data_list = []
    api_names_list = []

    # Traverse the DAG tasks to extract API names and parameters
    for template in yaml_data['spec']['templates']:
        if 'dag' in template and 'tasks' in template['dag']:
            for task in template['dag']['tasks']:
                api_name = task['name']
                parameters = {}

                # Extract parameters if they exist in the arguments
                if 'arguments' in task and 'parameters' in task['arguments']:
                    for param in task['arguments']['parameters']:
                        param_name = param['name']
                        param_value = param['value']
                        parameters[param_name] = param_value

                # Append each API and parameters as an entry
                api_data_list.append({
                    'api': api_name,
                    'parameters': parameters
                })

                api_names_list.append(api_name)

    # Convert the API data list to a JSON-like string format for "value"
    gold_data["gold_data"]["conversations"][0]["value"] = json.dumps(api_data_list)
    gold_data["gold_data"]["topology"] = api_names_list

    return gold_data

def process_folders(input_base_path, output_base_path):
    """
    Process all YAML files in the level folders and generate ground truth JSONL files.
    """
    levels = ["level1", "level2", "level3"]
    for level in levels:
        input_dir = os.path.join(input_base_path, level)
        output_file = os.path.join(output_base_path, f"gt_{level}.jsonl")

        results = []

        # Iterate over all YAML files in the directory
        for filename in os.listdir(input_dir):
            if filename.endswith(".yaml"):
                file_path = os.path.join(input_dir, filename)
                
                # Extract unique Id from the filename
                unique_id = int(filename.split('_')[-1].split('.')[0])
                
                # Generate ground truth data
                gold_data = generate_ground_truth(file_path, unique_id)
                results.append(gold_data)

        # Write all results to the JSONL file
        with open(output_file, 'w') as output:
            for result in results:
                json.dump(result, output)
                output.write('\n')

        print(f"Processed {len(results)} files for {level} and saved to {output_file}")

# Input and output directories
input_base_path = "./eval/data/gt/"
output_base_path = "./eval/data/gt/"

process_folders(input_base_path, output_base_path)
