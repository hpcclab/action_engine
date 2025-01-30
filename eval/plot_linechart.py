import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import pandas as pd
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

file_path = "/home/UNT/ae0589/project/action_engine/eval/scores/dag_scores.json" 
with open(file_path, 'r') as file:
    data = json.load(file)

records = []
for entry in data:
    timestamp = entry["timestamp"]
    for score in entry["scores"]:
        for method, results in score.items():
            for level, metrics in results["results"].items():
                for metric, values in metrics.items():
                    records.append({
                        "timestamp": timestamp,
                        "method": method,
                        "level": level,
                        "metric": metric,
                        "value": values["value"],
                        "ci_lower": values["confidence_interval"][0],
                        "ci_upper": values["confidence_interval"][1]
                    })

df = pd.DataFrame(records)


unique_timestamps = df["timestamp"].unique()
print(unique_timestamps)

timestamp_labels = {
    "2025-01-15 19:58:40": "top-10",
    "2025-01-15 19:56:53": "top-20",
    "2025-01-15 19:54:42": "top-30",
    "2025-01-16 10:29:38": "top-40",
}

df["label"] = df["timestamp"].map(timestamp_labels)

df_filtered = df[~df["method"].isin(["ZeroShot", "ZeroShot CoT"])]
df_filtered = df_filtered[df_filtered["metric"].isin(["F1_api", "F1_param", "topological_ordering_accuracy"])]
df_filtered.drop(columns=["timestamp"], inplace=True)
df_filtered.drop(columns=["ci_lower", "ci_upper"], inplace=True)
label_order = ["top-10", "top-20", "top-30", "top-40"]
df_filtered["label"] = pd.Categorical(df_filtered["label"], categories=label_order, ordered=True)
df_filtered = df_filtered.sort_values(by="label")



# -------------------------------------------------------------------------
# Global RC settings
# -------------------------------------------------------------------------
mpl.rcParams['font.size'] = 15
mpl.rcParams['axes.labelsize'] = 15
mpl.rcParams['axes.titlesize'] = 15
mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 15
mpl.rcParams['legend.fontsize'] = 15
mpl.rcParams['font.weight'] = "black"
mpl.rcParams['axes.labelweight'] = "black"
mpl.rcParams['axes.titleweight'] = "black"

# Embed-friendly
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

# -------------------------------------------------------------------------
# Metrics and label mapping
# -------------------------------------------------------------------------
metrics = ["F1_api", "F1_param", "topological_ordering_accuracy"]
metric_mapping = {
    "P_api": "Precision - Function Selection",
    "R_api": "Recall - Function Selection",
    "F1_api": "F1 - Function Selection",
    "P_param": "Precision - Parameter",
    "R_param": "Recall - Parameter",
    "F1_param": "F1 - Parameter",
    "topological_ordering_accuracy": "LCD - Topological Order"
}

level = "testdata_level3"
output_dir = "/home/UNT/ae0589/project/action_engine/eval/plots/linechart/"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------------------
# Style parameters
# -------------------------------------------------------------------------
linecols = ['red', 'mediumblue', 'green', 'purple']
line_styles = ['x-', 'o--', 'D-.', 's:']
marker_size = 8
linewidth = 3
method_order = ["FewShot", "FewShot CoT", "Action Engine", "Reverse Chain"]

# Suppose df_filtered is your DataFrame
# df_filtered = ...

# -------------------------------------------------------------------------
# Plot loop
# -------------------------------------------------------------------------
for metric in metrics:
    # Filter data
    subset = df_filtered[(df_filtered["level"] == level) & (df_filtered["metric"] == metric)]

    # Main figure
    fig, ax = plt.subplots(figsize=(6, 4))

    # Plot each method
    for i, method in enumerate(method_order):
        df_method = subset[subset["method"] == method]

        plt.plot(
            df_method["label"], 
            df_method["value"],
            line_styles[i],
            color=linecols[i],
            linewidth=linewidth,
            markersize=marker_size,
            label=method
        )

    ax.set_ylim(0, 0.5)
    ax.set_ylabel(metric_mapping[metric], fontsize=20, labelpad=10, weight='bold')
    ax.set_xlabel("", fontsize=15, weight="bold")
    plt.grid(True, alpha=0.3)

    # Main legend in the upper left; you can also remove it if desired
    # main_legend = ax.legend(loc='upper left', frameon=False)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save the main plot
    output_file_pdf = os.path.join(output_dir, f"{metric}.pdf")
    plt.savefig(output_file_pdf, format='pdf', dpi=600, 
                bbox_inches='tight', transparent=True)

    # --------------------------------------------------------
    # Save the legend only, aligned horizontally in one row
    # --------------------------------------------------------
    # Extract handles and labels from the current legend
    handles, labels = ax.get_legend_handles_labels()

    # Create a new figure for the legend only
    fig_legend = plt.figure(figsize=(6, 1.2))  # wider than it is tall
    # Put the legend in the center, single row with ncol=4
    fig_legend.legend(
        handles,
        labels,
        loc='center',
        frameon=False,
        ncol=len(method_order),     # 4 methods → 4 columns
        columnspacing=1.5,         # adjust spacing between legend entries
        handlelength=2,            # length of the line in the legend
        handletextpad=1            # space between line/marker and text
    )

# Save the legend PDF
legend_file_pdf = os.path.join(output_dir, f"legend.pdf")
fig_legend.savefig(legend_file_pdf, format='pdf', dpi=600,
                    bbox_inches='tight', transparent=True)

# Close
plt.close(fig_legend)

# Show or close the main plot
plt.show()
plt.close(fig)