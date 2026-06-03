import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load scores
scores_df = pd.read_excel("scores_for_predictions.xlsx")

# Columns to plot
score_cols = {
    "MV": "Normalized majority_voting_score",
    "Hishigaki": "Normalized hishigaki_score",
    "FF": "Normalized functional_flow_score",
    "RWR": "Normalized rwr",
    "Ensemble": "Total Score"
}

# Rank nodes by ensemble score
scores_df = scores_df.sort_values("Total Score", ascending=False).reset_index(drop=True)

# Create x-axis as node rank
scores_df["Node Rank"] = np.arange(1, len(scores_df) + 1)

# Smoothing window (adjustable)
window = 300  # increase for smoother curve

plt.figure(figsize=(12, 7))

for label, col in score_cols.items():
    smooth_score = scores_df[col].rolling(window, center=True).mean()
    plt.plot(
        scores_df["Node Rank"],
        smooth_score,
        label=label,
        linewidth=3
    )

plt.xlabel("Node Rank (sorted by Ensemble Score)")
plt.ylabel("Normalized Score")
plt.title("Score Trends Across Network Nodes")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("score_trends_across_nodes.png")
plt.show()
