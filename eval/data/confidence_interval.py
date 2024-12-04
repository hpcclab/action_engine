import json
import os
from datetime import datetime
import numpy as np


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
    input_str = input_str.replace("'", "\"")
    return input_str

def longest_common_subsequence(X, Y):
    """Computes the length of the Longest Common Subsequence (LCS) between two lists."""
    m = len(X)
    n = len(Y)
    # Create a matrix to store lengths of longest common suffixes
    L = [[0] * (n + 1) for i in range(m + 1)]
  
    # Build the LCS matrix
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1] == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
  
    # Length of the LCS is L[m][n]
    return L[m][n]

def calculate_topological_lcs_score(gold_topology, predict_topology):
    """Calculates a topological correctness score using LCS, enforcing order sensitivity."""
    lcs_length = longest_common_subsequence(gold_topology, predict_topology)
    max_length = max(len(gold_topology), len(predict_topology))
    return lcs_length / max_length if max_length > 0 else 0

def calculate_score_ToolLearning_from_data(raw_dataset):
    """Calculates the scores from the given dataset."""
    result_dict = {}

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
            
            gold_apis = [api['api'] for api in gold_answer]
            predicted_apis = [api['api'] for api in predict_answer]
            
            for predict_api in predict_answer:
                if "api" in predict_api:
                    predict_api_num += 1
                    if "parameters" in predict_api and isinstance(predict_api["parameters"], dict):
                        predict_param_num += len(predict_api["parameters"])
                    gold_idx = -1
                    for idx in range(len(gold_answer)):
                        if gold_answer[idx]["api"] == predict_api["api"]:
                            gold_idx = idx
                            break
                    if gold_idx != -1:
                        correct_api_num += 1
                        for parameter_name in predict_api["parameters"]:
                            if parameter_name in gold_answer[gold_idx]["parameters"] and str(predict_api["parameters"][parameter_name]) == str(gold_answer[gold_idx]["parameters"][parameter_name]):
                                correct_param_num += 1

        if 'topology' in data['gold_data'] and len(data['predict']) > 1 and isinstance(data['predict'][1], dict) and 'topology' in data['predict'][1]:
            gold_topology = data['gold_data']['topology']
            predict_topology = data['predict'][1]['topology']
            topological_accuracy_score = calculate_topological_lcs_score(gold_topology, predict_topology)
            topological_score_sum += topological_accuracy_score
            topological_score_count += 1
        else:
            print("NO TOPOLOGY")

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

def calculate_score_ToolLearning(data_path):
    """Reads data from a file and calculates the scores."""
    raw_dataset = read_jsonl(data_path)
    return calculate_score_ToolLearning_from_data(raw_dataset)

def bootstrap_confidence_interval(data, metric_function, n_bootstrap=1000, alpha=0.05):
    """
    Calculates a confidence interval for a given metric using bootstrapping.
    
    Parameters:
    - data: The dataset (list of dictionaries).
    - metric_function: Function to compute the metric.
    - n_bootstrap: Number of bootstrap samples.
    - alpha: Significance level for the confidence interval (default 0.05 for 95% CI).
    
    Returns:
    - mean_metric: Mean value of the metric across bootstrap samples.
    - ci_lower: Lower bound of the confidence interval.
    - ci_upper: Upper bound of the confidence interval.
    """
    scores = []
    for _ in range(n_bootstrap):
        # Resample the data with replacement
        bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_sample = bootstrap_sample.tolist()  # Convert ndarray to list
        # Calculate the metric for the bootstrap sample
        score = metric_function(bootstrap_sample)
        scores.append(score)

    scores = np.sort(scores)
    ci_lower = np.percentile(scores, 100 * (alpha / 2))
    ci_upper = np.percentile(scores, 100 * (1 - alpha / 2))
    mean_metric = np.mean(scores)
    return mean_metric, ci_lower, ci_upper

def calculate_score_ToolLearning_with_CI(data_path, n_bootstrap=1000, alpha=0.05):
    raw_dataset = read_jsonl(data_path)

    # Compute initial results
    result_dict = calculate_score_ToolLearning_from_data(raw_dataset)

    # Define bootstrap metric functions
    metrics = {
        "P_api": lambda data: calculate_score_ToolLearning_from_data(data)["P_api"],
        "R_api": lambda data: calculate_score_ToolLearning_from_data(data)["R_api"],
        "F1_api": lambda data: calculate_score_ToolLearning_from_data(data)["F1_api"],
        "P_param": lambda data: calculate_score_ToolLearning_from_data(data)["P_param"],
        "R_param": lambda data: calculate_score_ToolLearning_from_data(data)["R_param"],
        "F1_param": lambda data: calculate_score_ToolLearning_from_data(data)["F1_param"],
        "topological_ordering_accuracy": lambda data: calculate_score_ToolLearning_from_data(data)["topological_ordering_accuracy"]
    }

    # Calculate confidence intervals for each metric
    ci_results = {}
    for metric_name, metric_function in metrics.items():
        _, ci_lower, ci_upper = bootstrap_confidence_interval(
            raw_dataset, metric_function, n_bootstrap=n_bootstrap, alpha=alpha
        )
        ci_results[metric_name] = {"CI_lower": ci_lower, "CI_upper": ci_upper}

    # Combine results and CIs
    combined_results = {
        "scores": result_dict,
        "confidence_intervals": ci_results
    }
    return combined_results

def process_all_files_with_CI(input_dir, output_file, config_name, n_bootstrap=1000, alpha=0.05):
    """
    Processes all JSONL files in a directory, calculates scores and confidence intervals, 
    and appends the results under the specified configuration name in the output file.

    Parameters:
    - input_dir (str): Path to the directory containing input JSONL files.
    - output_file (str): Path to the output JSON file for storing results.
    - config_name (str): Name of the configuration (e.g., "ZeroShot CoT", "Action Engine").
    - n_bootstrap (int): Number of bootstrap samples for confidence intervals.
    - alpha (float): Significance level for confidence intervals.
    """

    levels = ["testdata_level1.jsonl", "testdata_level2.jsonl", "testdata_level3.jsonl"]
    results = {}
    for level_file in levels:
        input_path = os.path.join(input_dir, level_file)
        level_name = os.path.splitext(level_file)[0]
        result_with_ci = calculate_score_ToolLearning_with_CI(input_path, n_bootstrap=n_bootstrap, alpha=alpha)
        print(f"Results for {config_name} - {level_name}:")
        print(result_with_ci)
        results[level_name] = result_with_ci

    # Add a timestamp to the results
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        config_name: [
            {
                "timestamp": timestamp,
                "results": results
            }
        ]
    }

    # Append to the file
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        try:
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    print(f"Warning: {output_file} contains invalid JSON structure. Resetting to an empty list.")
                    existing_data = []
        except json.JSONDecodeError:
            print(f"Warning: {output_file} contains invalid JSON. Starting fresh.")
            existing_data = []
    else:
        existing_data = []

    # Add the new entry to the data
    existing_data.append(entry)

    # Save back the updated data
    with open(output_file, 'w') as f:
        json.dump(existing_data, f, indent=4)

    print(f"Results for {config_name} saved to {output_file}")


# Process with confidence intervals
input_dir = "./eval/data/predict/LLMs/ZeroShot/gpt-4o/"
output_file = "./eval/dag_scores_with_CI.json"
process_all_files_with_CI(input_dir, output_file, config_name="ZeroShot CoT", n_bootstrap=1000, alpha=0.05)

input_dir = "./eval/data/predict/LLMs/FewShot/gpt-4o/"
process_all_files_with_CI(input_dir, output_file, config_name="FewShot CoT", n_bootstrap=1000, alpha=0.05)

input_dir = "./eval/data/predict/AE/gpt-4o/"
process_all_files_with_CI(input_dir, output_file, config_name="Action Engine", n_bootstrap=1000, alpha=0.05)
