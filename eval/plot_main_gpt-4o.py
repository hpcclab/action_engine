import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# Optional: Use Seaborn style for better aesthetics
plt.style.use("seaborn-v0_8-whitegrid")

# Adjust global font settings
mpl.rcParams["font.size"] = 60
mpl.rcParams["axes.labelsize"] = 50
mpl.rcParams["axes.titlesize"] = 50
mpl.rcParams["xtick.labelsize"] = 50
mpl.rcParams["ytick.labelsize"] = 60
mpl.rcParams["legend.fontsize"] = 60
mpl.rcParams["font.weight"] = "black"
mpl.rcParams["axes.labelweight"] = "black"
mpl.rcParams["axes.titleweight"] = "black"

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
    "P_api": "Precision",
    "R_api": "Recall",
    "F1_api": "F1",
    "P_param": "Precision",
    "R_param": "Recall",
    "F1_param": "F1",
    "topological_ordering_accuracy": "LCD"
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

# Create a discrete color map for the number of methods
num_methods = 6
colors = plt.cm.get_cmap("tab10", num_methods)

color_mapping = {
    "ZeroShot (GPT-4o)": colors(0),  
    "ZeroShot CoT (GPT-4o)": colors(1),  
    "FewShot (GPT-4o)": colors(2), 
    "FewShot CoT (GPT-4o)": colors(3),  
    "Action Engine": colors(4),  
    "Reverse Chain": colors(5),  
}

# Default color for methods not in the mapping
default_color = "#7f7f7f"  # Gray as fallback

# Process the data for each metric
for metric in metrics:
    fig, ax = plt.subplots(figsize=(16, 8))  # Larger figure size
    x = np.arange(len(levels))
    width = 0.15  # Adjust bar width as needed

    for i, score in enumerate(data):
        method = list(score.keys())[0]
        method_data = score[method]["results"]

        values = [method_data[level][metric]["value"] for level in levels]
        ci_lower = [method_data[level][metric]["confidence_interval"][0] for level in levels]
        ci_upper = [method_data[level][metric]["confidence_interval"][1] for level in levels]

        # Convert to numpy arrays for easier calculations
        values_arr = np.array(values)
        lower_err = values_arr - np.array(ci_lower)
        upper_err = np.array(ci_upper) - values_arr

        # Determine the color for the method
        bar_color = color_mapping.get(method, default_color)

        # Plot bars with error bars for confidence intervals
        ax.bar(
            x + i * width,
            values_arr,
            width,
            label=method,
            yerr=[lower_err, upper_err],
            capsize=8,  # Larger cap size
            color=bar_color,  # Use the predefined color for this method
            edgecolor="black"
        )
    # Customize the plot for the current metric
    ax.set_xlabel("Level of Dataset", fontsize=43, labelpad=10, weight='bold')
    ax.set_ylabel(metric_mapping[metric], fontsize=43, labelpad=10, weight='bold')
    ax.set_xticks(x + (num_methods - 1) * width / 2)
    ax.set_xticklabels([level_mapping[level] for level in levels], fontsize=43)

    # Set y-axis limit conditionally
    if metric in ["P_param", "R_param", "F1_param"]:
        ax.set_yticks([0.0, 0.2, 0.4])
        ax.set_ylim(0, 0.4)  # Explicitly set the y-axis range        
 # Adjust y-axis max to 0.4 for specific metrics
    else:
        ax.set_yticks([0.0, 0.2, 0.4, 0.6])
        ax.set_ylim(0, 0.6)  # Force y-axis to range from 0 to 1
  # Default y-axis max
    ax.grid(True, linestyle="--", alpha=0.6)
    

    # Tight layout and save the plot
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    # Save as PDF
    output_file_pdf = os.path.join(output_dir, f"{metric}.pdf")
    plt.savefig(output_file_pdf, format='pdf', dpi=600, bbox_inches='tight')  # High DPI for clear text
    plt.close(fig)

# Create a standalone figure for the legend
fig, ax = plt.subplots(figsize=(6, 1.2))  # Adjust size to fit all legend entries
ax.axis('off')  # Turn off the axes

# Extract colors assigned to methods and create a legend with method names
handles = []
for method, color in color_mapping.items():
    handles.append(
        mpl.patches.Patch(
            color=color, label=method  # Use the consistent color and method name
        )
    )

# Add the legend to the figure
legend = ax.legend(
    handles=handles,
    loc="center",
    bbox_to_anchor=(0.5, 0.5),
    ncol=len(color_mapping),  # Number of columns
    fontsize=40,       # Match your plot font size
    frameon=False      # Remove the legend frame for consistency
)

# Save the legend as a standalone PDF
output_file_pdf = os.path.join(output_dir, "legend.pdf")
plt.savefig(output_file_pdf, format='pdf', dpi=600, bbox_inches='tight')  # High DPI for clear text
plt.close(fig)