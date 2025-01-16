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
methods = ["FewShot", "FewShot CoT", "Action Engine", "Reverse Chain"]
metrics = ["F1_api", "F1_param"]  # Customize metrics if needed
levels = ["testdata_level1", "testdata_level2", "testdata_level3"]

# Prepare data for plotting
plot_data = {metric: {method: [] for method in methods} for metric in metrics}
ci_data = {metric: {method: [] for method in methods} for metric in metrics}

# Process data
for idx, experiment in enumerate(experiment_results):
    for method in methods:
        index = methods.index(method)
        for metric in metrics:
            if method in experiment["scores"][index]:
                print(method)
                method_results = experiment["scores"][index][method].get("results", {})
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
                    print(len(values))
                    plot_data[metric][method].append(np.mean(values))
                    ci_data[metric][method].append(np.mean(confidence_intervals))
print(plot_data)
# Ensure data consistency: Pad missing data to match the length of top_k_values
for metric in metrics:
    for method in methods:
        mean_values = plot_data[metric][method]
        ci_values = ci_data[metric][method]
        if len(mean_values) < len(top_k_values):
            missing_count = len(top_k_values) - len(mean_values)
            mean_values.extend([None] * missing_count)
            ci_values.extend([None] * missing_count)

# Visualization
fig, axes = plt.subplots(1, len(metrics), figsize=(24, 8), sharey=False)
colors = sns.color_palette("tab10", len(methods))

for ax, metric in zip(axes, metrics):
    for i, method in enumerate(methods):
        mean_values = plot_data[metric][method]
        ci_values = ci_data[metric][method]
        
        # Filter out None values
        valid_indices = [idx for idx, val in enumerate(mean_values) if val is not None]
        filtered_top_k = [top_k_values[idx] for idx in valid_indices]
        filtered_means = [mean_values[idx] for idx in valid_indices]
        filtered_cis = [ci_values[idx] for idx in valid_indices]
        
        if filtered_top_k:  # Check if there is data to plot
            ax.plot(filtered_top_k, filtered_means, label=method, color=colors[i], marker='o', linewidth=2)
            ax.fill_between(
                filtered_top_k,
                np.array(filtered_means) - np.array(filtered_cis),
                np.array(filtered_means) + np.array(filtered_cis),
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
output_file_pdf = os.path.join(output_dir, "ablation_results_topk.pdf")
plt.savefig(output_file_pdf, format='pdf', dpi=600, bbox_inches='tight')  # High DPI for clear text
plt.close(fig)