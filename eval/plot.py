import json
import matplotlib.pyplot as plt
import numpy as np

# Load the JSON data
file_path = './eval/scores/dag_scores.json'  # Replace with your file path
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract the scores data
data = data[0]["scores"]
levels = ["testdata_level1", "testdata_level2", "testdata_level3"]
methods = ["ZeroShot CoT", "FewShot CoT", "Action Engine"]

# List of all metrics to plot
metrics = [
    "P_api", "R_api", "F1_api",
    "P_param", "R_param", "F1_param",
    "topological_ordering_accuracy"
]

# Directory to save plots
output_dir = "./eval/plots/"
import os
os.makedirs(output_dir, exist_ok=True)

# Process the data for each metric
for metric in metrics:
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(levels))
    width = 0.25  # Bar width

    for i, score in enumerate(data):
        method = list(score.keys())[0]
        method_data = score[method]["results"]

        values = [method_data[level][metric]["value"] for level in levels]
        ci_lower = [method_data[level][metric]["confidence_interval"][0] for level in levels]
        ci_upper = [method_data[level][metric]["confidence_interval"][1] for level in levels]

        # Plot bars with error bars for confidence intervals
        ax.bar(
            x + i * width,
            values,
            width,
            label=method,
            yerr=[np.array(values) - np.array(ci_lower), np.array(ci_upper) - np.array(values)],
            capsize=5,
        )

    # Customize the plot for the current metric
    ax.set_xlabel("Levels")
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} Scores with Confidence Intervals")
    ax.set_xticks(x + width)
    ax.set_xticklabels(levels)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)

    # Scale y-axis to a maximum of 1
    ax.set_ylim(0, 1)

    # Save the plot as an image
    output_file = os.path.join(output_dir, f"{metric}.png")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close(fig)  # Close the figure to save memory
