import json
import os
import numpy as np
import random
from datetime import datetime

# Utility Functions
def read_jsonl(file_path):
    """Reads a JSONL file and returns a list of JSON objects (dictionaries)."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                data.append(json.loads(line))  # Each line is read and parsed into a dictionary
    return data

def escape_json(input_str):
    """Converts a JSON-like string to a valid JSON string."""
    return input_str.replace("'", "\"")

def longest_common_subsequence(X, Y):
    """Computes the length of the Longest Common Subsequence (LCS) between two lists."""
    m, n = len(X), len(Y)
    # Create a matrix to store lengths of longest common suffixes
    L = [[0] * (n + 1) for _ in range(m + 1)]

    # Build the LCS matrix
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1] == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    return L[m][n]

def calculate_topological_lcs_score(gold_topology, predict_topology):
    """Calculates a topological correctness score using LCS, enforcing order sensitivity."""
    lcs_length = longest_common_subsequence(gold_topology, predict_topology)
    max_length = max(len(gold_topology), len(predict_topology))
    return lcs_length / max_length if max_length > 0 else 0

# Core Functions
def calculate_metrics(raw_dataset):
    """Calculates evaluation scores for ToolLearning given the dataset."""
    correct_format_num = 0
    correct_api_num = 0
    predict_api_num = 0
    gold_api_num = 0
    correct_param_num = 0
    predict_param_num = 0
    gold_param_num = 0

    topological_score_sum = 0
    topological_score_count = 0

    for data in raw_dataset:
        gold_answer_str = data['gold_data']["conversations"][0]["value"]
        gold_answer = json.loads(escape_json(gold_answer_str))
        gold_api_num += len(gold_answer)
        
        for gold_api in gold_answer:
            gold_param_num += len(gold_api['parameters'])

        if data['predict'] and isinstance(data['predict'][0], list) and len(data['predict'][0]) > 0:
            predict_answer = data['predict'][0]
            correct_format_num += 1

            for predict_api in predict_answer:
                if "api" in predict_api:
                    predict_api_num += 1
                    if "parameters" in predict_api and isinstance(predict_api["parameters"], dict):
                        predict_param_num += len(predict_api["parameters"])
                    gold_idx = next(
                        (idx for idx, gold in enumerate(gold_answer) if gold["api"] == predict_api["api"]), -1
                    )
                    if gold_idx != -1:
                        correct_api_num += 1
                        for param_name, param_value in predict_api["parameters"].items():
                            if (
                                param_name in gold_answer[gold_idx]["parameters"]
                                and str(param_value) == str(gold_answer[gold_idx]["parameters"][param_name])
                            ):
                                correct_param_num += 1

        if 'topology' in data['gold_data'] and len(data['predict']) > 1 and isinstance(data['predict'][1], dict):
            gold_topology = data['gold_data']['topology']
            predict_topology = data['predict'][1]['topology']
            topological_accuracy_score = calculate_topological_lcs_score(gold_topology, predict_topology)
            topological_score_sum += topological_accuracy_score
            topological_score_count += 1
        else:
            if 'topology' not in data['gold_data']:
                print("noo topology in ground truth")
            if not len(data['predict']) > 1:
                print("length of prediction smaller than 1")
            print(data['Id'])

    result_dict = {}
    result_dict["AMOUNT"] = correct_format_num / len(raw_dataset)
    result_dict["P_api"] = correct_api_num / predict_api_num if predict_api_num > 0 else 0.0
    result_dict["R_api"] = correct_api_num / gold_api_num if gold_api_num > 0 else 0.0
    result_dict["F1_api"] = (
        2 * result_dict["P_api"] * result_dict["R_api"] / (result_dict["P_api"] + result_dict["R_api"])
        if result_dict["P_api"] > 0 and result_dict["R_api"] > 0
        else 0.0
    )
    result_dict["P_param"] = correct_param_num / predict_param_num if predict_param_num > 0 else 0.0
    result_dict["R_param"] = correct_param_num / gold_param_num if gold_param_num > 0 else 0.0
    result_dict["F1_param"] = (
        2 * result_dict["P_param"] * result_dict["R_param"] / (result_dict["P_param"] + result_dict["R_param"])
        if result_dict["P_param"] > 0 and result_dict["R_param"] > 0
        else 0.0
    )
    result_dict["topological_ordering_accuracy"] = (
        topological_score_sum / topological_score_count if topological_score_count > 0 else 0.0
    )

    return result_dict

def calculate_confidence_intervals(raw_dataset, num_bootstrap_samples=1000):
    """
    Calculates confidence intervals for all metrics using bootstrapping.
    """
    metrics_list = []

    for _ in range(num_bootstrap_samples):
        # Resample the dataset with replacement
        bootstrap_sample = [random.choice(raw_dataset) for _ in range(len(raw_dataset))]
        # Compute metrics for the bootstrap sample
        metrics = calculate_metrics(bootstrap_sample)
        metrics_list.append(metrics)

    # Calculate confidence intervals
    metrics_keys = metrics_list[0].keys()
    confidence_intervals = {}

    for key in metrics_keys:
        metric_values = [metrics[key] for metrics in metrics_list]
        lower = np.percentile(metric_values, 2.5)
        upper = np.percentile(metric_values, 97.5)
        confidence_intervals[key] = {'95% CI': (lower, upper)}

    return confidence_intervals

def process_all_files(input_dir, all_data, config_name, num_bootstrap_samples=1000):
    """
    Processes all JSONL files in a directory, calculates scores and confidence intervals for each level,
    and appends the results under the specified configuration name.
    """
    levels = ["testdata_level1.jsonl", "testdata_level2.jsonl", "testdata_level3.jsonl"]
    results = {}

    for level_file in levels:
        input_path = os.path.join(input_dir, level_file)
        level_name = os.path.splitext(level_file)[0]

        # Read the dataset
        raw_dataset = read_jsonl(input_path)
        print("*"*40)
        print(len(raw_dataset))
        # Compute point estimates
        point_estimate = calculate_metrics(raw_dataset)

        # Compute confidence intervals
        confidence_intervals = calculate_confidence_intervals(raw_dataset, num_bootstrap_samples)

        # Combine point estimates and confidence intervals
        combined_results = {}
        for key in point_estimate.keys():
            combined_results[key] = {
                'value': point_estimate[key],
                'confidence_interval': confidence_intervals[key]['95% CI']
            }

        results[level_name] = combined_results

    entry = {
        config_name: {"results": results}
    }
    print(f"Results for {config_name} saved")
    all_data.append(entry)

# Main Execution
def main():
    all_data = []
    output_file = "./eval/scores/dag_scores.json"

    # Process configurations
    configurations = {
        "ZeroShot CoT": "./eval/data/predict/LLMs/ZeroShot/gpt-4o/",
        "FewShot CoT": "./eval/data/predict/LLMs/FewShot/gpt-4o/",
        "Action Engine": "./eval/data/predict/AE/gpt-3.5-turbo/"
    }

    for config_name, input_dir in configurations.items():
        process_all_files(input_dir, all_data, config_name, num_bootstrap_samples=1000)

    # Load existing data if present
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        try:
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    print(f"Warning: Invalid JSON structure in {output_file}. Resetting to an empty list.")
                    existing_data = []
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {output_file}. Starting fresh.")
            existing_data = []
    else:
        existing_data = []

    # Add new results with a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing_data.insert(0, {"timestamp": timestamp, "scores": all_data})

    # Save the updated data
    with open(output_file, 'w') as f:
        json.dump(existing_data, f, indent=4)

# Entry Point
if __name__ == "__main__":
    main()