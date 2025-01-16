import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import json
import os
# Optional: Use Seaborn style for better aesthetics
plt.style.use("seaborn-v0_8-whitegrid")

# Load the JSON data
file_path = './eval/scores/dag_scores.json'  # Replace with your file path
with open(file_path, 'r') as file:
    experiment_results = json.load(file)

# Extract scores for each top-k value
top_k_values = [10, 20, 30]  # Adjust as needed
methods = ["ZeroShot", "ZeroShot CoT","FewShot", "FewShot CoT", "Action Engine", "Reverse Chain"]
metrics = ["P_api", "R_api", "F1_api"]  # Customize metrics if needed
levels = ["testdata_level1", "testdata_level2", "testdata_level3"]

# Prepare data for plotting
plot_data = {metric: {method: [] for method in methods} for metric in metrics}
ci_data = {metric: {method: [] for method in methods} for metric in metrics}

for idx, experiment in enumerate(experiment_results):
    for method in methods:
        for metric in metrics:
            print(f"idx {idx} - {metric} - {method}: {plot_data[metric][method]}")
            if method in experiment["scores"][0]:
                method_results = experiment["scores"][0][method].get("results", {})
                if method_results:  # Check if results exist
                    values = []
                    confidence_intervals = []
                    for level in levels:
                        if level in method_results:
                            metric_data = method_results[level].get(metric, {})
                            if "value" in metric_data and "confidence_interval" in metric_data:
                                value = metric_data["value"]
                                ci = metric_data["confidence_interval"]
                                values.append(value)
                                confidence_intervals.append((ci[1] - ci[0]) / 2)  # Half-width for error bands
                    if values:  # Ensure we have values before calculating mean
                        plot_data[metric][method].append(np.mean(values))
                        ci_data[metric][method].append(np.mean(confidence_intervals))

# Visualization
fig, axes = plt.subplots(1, len(metrics), figsize=(24, 8), sharey=False)
colors = sns.color_palette("tab10", len(methods))

for ax, metric in zip(axes, metrics):
    for i, method in enumerate(methods):
        if method in plot_data[metric]:
            mean_values = plot_data[metric][method]
            ci_values = ci_data[metric][method]
            ax.plot(top_k_values, mean_values, label=method, color=colors[i], marker='o', linewidth=2)
            ax.fill_between(
                top_k_values,
                np.array(mean_values) - np.array(ci_values),
                np.array(mean_values) + np.array(ci_values),
                color=colors[i],
                alpha=0.2
            )
    ax.set_title(f"{metric} over Top-k", fontsize=18, weight='bold')
    ax.set_xlabel("Top-k Values", fontsize=14)
    ax.set_ylabel(f"{metric} Score", fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True)

# Adjust layout and save the figure
plt.tight_layout()

# Directory to save plots
output_dir = "./eval/plots/linechart/"  
os.makedirs(output_dir, exist_ok=True)
# Save the legend as a standalone PDF
output_file_pdf = os.path.join(output_dir, "ablation_results_topk.pdf")
plt.savefig(output_file_pdf, format='pdf', dpi=600, bbox_inches='tight')  # High DPI for clear text
plt.close(fig)