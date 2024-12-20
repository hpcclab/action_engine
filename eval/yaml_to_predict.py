import os
import json
import yaml
import logging

# Set up logging
logging.basicConfig(
    filename='data_extraction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def read_jsonl(file_path):
    """Reads a JSONL file and returns a list of JSON objects (dictionaries)."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))  # Each line is read and parsed into a dictionary
    return data

def read_json(file_path):
    """Reads a JSON file and returns its content."""
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_predict_from_yaml(item):
    workflow = item["workflow"]

    # Check if the workflow is already a dictionary
    if isinstance(workflow, dict):
        yaml_data = workflow
    elif not isinstance(workflow, dict):
        # Parse the YAML string into a dictionary
        yaml_data = yaml.safe_load(workflow)
    else:
        logging.warning(f"YAML format error")    
    
    predict = []
    api_names_list = []

    # Traverse the DAG tasks to extract API names and parameters
    for template in yaml_data['spec']['templates']:
        if 'dag' in template and 'tasks' in template['dag']:
            task_list = []
            for task in template['dag']['tasks']:
                api_name = task['template']
                parameters = {}

                # Extract parameters if they exist in the arguments
                if 'arguments' in task and 'parameters' in task['arguments']:
                    for param in task['arguments']['parameters']:
                        param_name = param['name']
                        param_value = param['value']
                        parameters[param_name] = param_value

                # Add each API task to the predict list in the required format
                task_list.append({
                    'api': api_name,
                    'parameters': parameters
                })
                api_names_list.append(api_name)

            predict.append(task_list)  # Append the task list as a single prediction
            predict.append({"topology": api_names_list})  
    return predict

def process_files(gt_dir, pred_dir, output_dir):
    """Processes ground truth JSONL files and prediction YAML files."""
    for level in levels:
        # Define file paths
        gt_file = os.path.join(gt_dir, f"gt_{level}.jsonl")
        pred_file = os.path.join(pred_dir, f"{level}_result.json")
        output_file = os.path.join(output_dir, f"testdata_{level}.jsonl")

        # Load ground truth and prediction data
        gt_data = read_jsonl(gt_file)
        pred_data = read_json(pred_file)

        # Create a dictionary for quick access to prediction data by Id
        pred_dict = {item["Id"]: item for item in pred_data}
        # Match and add predictions to ground truth data
        updated_data = []
        for entry in gt_data:
            entry_id = entry["Id"]
            if entry_id in pred_dict:
                if pred_dict[entry_id]["status"] == "Success":
                    logging.info(f"Matched prediction for Id {entry_id}.")
                    try:
                        predict = generate_predict_from_yaml(pred_dict[entry_id])
                        if not predict:
                            logging.warning(f"No prediction was extracted at Id {entry_id}")    
                            continue
                        entry["predict"] = predict
                        updated_data.append(entry)
                    except Exception as e:
                        pass
                        # print(f"Skipping entry with Id {entry_id} due to error: {e}")
                else:
                    logging.warning(f"Prediction for Id {entry_id} has non-success status.")
            else:
                logging.warning(f"No prediction found for ground truth Id {entry_id}.")

        # Save the updated data to a new JSONL file
        with open(output_file, 'w') as f:
            for entry in updated_data:
                f.write(json.dumps(entry) + '\n')

        print(f"Processed {len(updated_data)} entries for {level} and saved to {output_file}")

def update_tasks_with_topology(data_list):
    """
    Update placeholders in the 'parameters' field of the predict section in a list of JSON objects
    by replacing `tasks.t{index+1}` with corresponding topology names.

    Parameters:
    - data_list (list): List of JSON-like dictionaries to process.

    Returns:
    - list: Updated list of JSON-like dictionaries.
    """
    updated_data_list = []
    for data in data_list:
        topology = data["predict"][-1]["topology"]  # Extract topology list
        predictions = data["predict"][0]  # Extract predictions list

        for pred in predictions:
            if "parameters" in pred:
                for key, value in pred["parameters"].items():
                    # Check if the value contains "tasks.t" and ensure it matches the expected format
                    if "tasks.t" in value:
                        try:
                            # Extract the index from the placeholder "t{index+1}"
                            index_str = value.split(".t")[1].split(".")[0]
                            if not index_str.isdigit():
                                raise ValueError(f"Invalid index format: {index_str}")
                            index = int(index_str) - 1
                            
                            if 0 <= index < len(topology):
                                # Replace the "t{index+1}" with the corresponding topology name
                                pred["parameters"][key] = value.replace(
                                    f"tasks.t{index+1}.result",
                                    f"tasks.{topology[index]}.result",
                                )
                        except Exception as e:
                            print(f"Error processing key '{key}' with value '{value}': {e}")
                            # Skip processing for this key-value pair if there's an error

        # Update the predictions back in the data
        data["predict"][0] = predictions
        updated_data_list.append(data)

    return updated_data_list


def write_jsonl(file_path, data):
    """
    Write a list of dictionaries to a JSONL file, with one dictionary per line.

    Parameters:
    - file_path (str): Path to the JSONL file.
    - data (list): List of dictionaries to write to the file.
    """
    with open(file_path, 'w') as file:  # Use 'w' to overwrite or 'a' to append
        for entry in data:
            file.write(json.dumps(entry) + '\n')



levels = ["level1", "level2", "level3"]

# # Zroshot CoT
gt_dir = "./eval/data/gt/"
pred_dir = "./eval/data/predict/LLMs/ZeroShot/gpt-4o/"
output_dir = "./eval/data/predict/LLMs/ZeroShot/gpt-4o/"
process_files(gt_dir, pred_dir, output_dir)

# # Zroshot CoT
gt_dir = "./eval/data/gt/"
pred_dir = "./eval/data/predict/LLMs/FewShot/gpt-4o/"
output_dir = "./eval/data/predict/LLMs/FewShot/gpt-4o/"
process_files(gt_dir, pred_dir, output_dir)

# Action Engine
gt_dir = "./eval/data/gt/"
pred_dir = "./eval/data/predict/AE/gpt-4o/"
output_dir = "./eval/data/predict/AE/gpt-4o/"
process_files(gt_dir, pred_dir, output_dir)
for level in levels:
    try:
        output_file = os.path.join(output_dir, f"testdata_{level}.jsonl")
        data = read_jsonl(output_file)  # Read JSONL file
        updated_data = update_tasks_with_topology(data)  # Update tasks with topology
        write_jsonl(output_file, updated_data)  # Write back updated data to the file
        logging.info(f"Processed and saved testdata_{level}.jsonl with {len(updated_data)} entries.")
    except Exception as e:
        logging.error(f"Error processing level {level}: {e}")

