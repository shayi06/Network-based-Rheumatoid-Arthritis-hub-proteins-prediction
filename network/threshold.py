import json
import numpy as np
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

# -------------------- Load Data --------------------
with open(r"D:\abi\abi\pythonProject\Abi 2025\Research\network\network\all_scores.json", "r") as f:
    data = json.load(f)

with open(r"D:\abi\abi\pythonProject\Abi 2025\Research\network\evaluation\algo_scores.json", "r") as f:
    algo_scores = json.load(f)

# -------------------- Build Labels --------------------
true_labels      = []
predicted_labels = []

for i in range(1, 11):
    fold_str = str(i)
    ps = data[fold_str]['test_seeds']

    for p in ps:
        true_labels.append(1)
        predicted_labels.append(algo_scores['Ensemble'][p])

    ns = list(set(data[fold_str]['MV']) - set(ps))
    for n in ns:
        true_labels.append(0)
        predicted_labels.append(algo_scores['Ensemble'][n])

true_labels      = np.array(true_labels)
predicted_labels = np.array(predicted_labels)

# -------------------- Best F1 Threshold --------------------
precision, recall, thresholds = precision_recall_curve(true_labels, predicted_labels)
f1_scores  = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-8)
best_idx   = np.argmax(f1_scores)
best_thr   = thresholds[best_idx]

print(f"Best Threshold : {best_thr:.4f}")
print(f"Precision      : {precision[best_idx]:.4f}")
print(f"Recall         : {recall[best_idx]:.4f}")
print(f"F1 Score       : {f1_scores[best_idx]:.4f}")

# -------------------- Apply Threshold --------------------
all_seeds = []
for i in range(1, 11):
    all_seeds += data[str(i)]['test_seeds']
all_seeds = list(set(all_seeds))

candidates       = {p: s for p, s in algo_scores['Ensemble'].items() if s >= best_thr}
known_recovered  = [p for p in candidates if p in all_seeds]
novel_candidates = sorted(candidates, key=candidates.get, reverse=True)
novel_candidates = [p for p in novel_candidates if p not in all_seeds]

print(f"\nTotal candidates  : {len(candidates)}")
print(f"Known seeds found : {len(known_recovered)}")
print(f"Novel RA proteins : {len(novel_candidates)}")
print(f"\nTop 20 novel RA candidates:")
for i, p in enumerate(novel_candidates[:20], 1):
    print(f"  {i:2}. {p}  (score={candidates[p]:.4f})")

# Best Threshold : 0.2209
# Precision      : 0.2186
# Recall         : 0.3534
# F1 Score       : 0.2701

# Total candidates  : 215
# Known seeds found : 47
# Novel RA proteins : 168