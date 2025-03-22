import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# Optional: Use Seaborn style for better aesthetics
plt.style.use("seaborn-v0_8-whitegrid")

# Adjust global font settings for readability
mpl.rcParams.update({
    "font.size": 34,
    "axes.labelsize": 34,
    "axes.titlesize": 34,
    "xtick.labelsize": 30,
    "ytick.labelsize": 30,
    "legend.fontsize": 30,
    "font.weight": "black",
    "axes.labelweight": "black",
    "axes.titleweight": "black",
})

# Load the JSON data
file_path = './eval/scores/dag_scores.json'  # Replace with your file path
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract the scores data
data = data[0]["scores"]

# Label mappings
level_mapping = {
    "testdata_level1": "Level - 1",
    "testdata_level2": "Level - 2",
    "testdata_level3": "Level - 3"
}
metric_mapping = {
    "P_api": "Precision - Function Selection",
    "R_api": "Recall - Function Selection",
    "F1_api": "F1 - Function Selection",
    "P_param": "Precision - Parameter",
    "R_param": "Recall - Parameter",
    "F1_param": "F1 - Parameter",
    "topological_ordering_accuracy": "LCD - Topological Order"
}
title_mapping = {
    "P_api": "Precision Score for\nFunction Selection",
    "R_api": "Recall Score for\nFunction Selection",
    "F1_api": "F1 Score for\nFunction Selection",
    "P_param": "Precision Score for\nParameter",
    "R_param": "Recall Score for\nParameter",
    "F1_param": "F1 Score for\nParameter",
    "topological_ordering_accuracy": "LCD Score for\nTopological Order"
}

levels = list(level_mapping.keys())
metrics = list(metric_mapping.keys())

# Directory to save plots
output_dir = "./eval/plots/"
os.makedirs(output_dir, exist_ok=True)

# Dynamically get all method names
method_names = [list(score.keys())[0] for score in data]
unique_methods = list(dict.fromkeys(method_names))  # preserve order
num_methods = len(unique_methods)

num_methods = 10
colors = plt.cm.get_cmap("tab10", num_methods)

nums = [5, 1, 7, 3, 0, 2, 4, 6, 8, 9]
color_mapping = {method: colors(nums[i]) for i, method in enumerate(unique_methods)}

# Fallback color
default_color = "#7f7f7f"

# Plotting loop
for metric in metrics:
    fig, ax = plt.subplots(figsize=(18, 8))
    x = np.arange(len(levels))
    width = 0.8 / num_methods  # Ensure all bars fit within category

    for i, method in enumerate(unique_methods):
        score = next((s for s in data if method in s), None)
        if not score:
            continue

        method_data = score[method]["results"]
        values = [method_data[level][metric]["value"] for level in levels]
        ci_lower = [method_data[level][metric]["confidence_interval"][0] for level in levels]
        ci_upper = [method_data[level][metric]["confidence_interval"][1] for level in levels]

        values_arr = np.array(values)
        lower_err = values_arr - np.array(ci_lower)
        upper_err = np.array(ci_upper) - values_arr

        bar_color = color_mapping.get(method, default_color)

        ax.bar(
            x + i * width,
            values_arr,
            width,
            label=method,
            yerr=[lower_err, upper_err],
            capsize=6,
            color=bar_color,
            edgecolor="black"
        )

    # Final plot adjustments
    ax.set_xlabel("Level of Dataset", labelpad=10)
    ax.set_ylabel(metric_mapping[metric], labelpad=10)
    ax.set_xticks(x + (num_methods / 2 - 0.5) * width)
    ax.set_xticklabels([level_mapping[level] for level in levels])
    ax.set_ylim(0, 0.6)  # Adjust if needed
    ax.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_file_pdf = os.path.join(output_dir, f"{metric}.pdf")
    plt.savefig(output_file_pdf, format='pdf', dpi=600)
    plt.close(fig)

# Create a standalone figure for the legend
fig, ax = plt.subplots(figsize=(20, 2.5))
ax.axis('off')

handles = [
    mpl.patches.Patch(color=color_mapping.get(method, default_color), label=method)
    for method in unique_methods
]

legend = ax.legend(
    handles=handles,
    loc="center",
    bbox_to_anchor=(0.5, 0.5),
    ncol=5 if num_methods >8  else num_methods,
    fontsize=30,
    frameon=False
)

output_file_pdf = os.path.join(output_dir, "legend.pdf")
plt.savefig(output_file_pdf, format='pdf', dpi=600, bbox_inches='tight')
plt.close(fig)
