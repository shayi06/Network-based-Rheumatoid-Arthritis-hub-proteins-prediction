from sklearn.metrics import precision_recall_curve, auc, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import json
from get_combined_scores import algo_scores

# Load all_scores.json for fold info
with open(r"D:\abi\abi\pythonProject\Abi 2025\Research\network\network\all_scores.json", "r") as file:
    data = json.load(file)

algos = ['MV', 'Hishi', 'RWR', 'FF', 'Ensemble']

precision_recall_data = {}
for algo in algos:
    precision_recall_data[algo] = {}

# exactly like repo
for algo in algos:
    true_labels      = []
    predicted_labels = []

    for i in range(1, 11):
        fold_str = str(i)

        # test seeds = positives (label=1)
        ps = data[fold_str]['test_seeds']
        for p in ps:
            true_labels.append(1)
            if algo == "Hishi":
                predicted_labels.append(algo_scores['Hishi'][p])
            else:
                predicted_labels.append(algo_scores[algo][p])

        # non-seeds = negatives (label=0)
        ns = list(set(data[fold_str]['MV']) - set(ps))
        for n in ns:
            true_labels.append(0)
            if algo == "Hishi":
                predicted_labels.append(algo_scores['Hishi'][n])
            else:
                predicted_labels.append(algo_scores[algo][n])

    # calculate metrics
    precision, recall, _ = precision_recall_curve(true_labels, predicted_labels)
    roc_auc              = roc_auc_score(true_labels, predicted_labels)
    fpr, tpr, _          = roc_curve(true_labels, predicted_labels)
    auc_pr               = auc(recall, precision)

    print(f'AUPR for {algo}: {auc_pr:.4f}')
    print(f'AUROC for {algo}: {roc_auc:.4f}')

    precision_recall_data[algo] = {
        'precision': list(precision),
        'recall'   : list(recall),
        'fpr'      : list(fpr),
        'tpr'      : list(tpr),
        'AUPR'     : auc_pr,
        'AUROC'    : roc_auc
    }

    with open('precision_recall_data.json', 'w') as file:
        json.dump(precision_recall_data, file, indent=4)

print("\n📊 Summary:")
print("=" * 50)
for algo in algos:
    print(f"{algo:<10} AUPR: {precision_recall_data[algo]['AUPR']:.4f} "
          f"| AUROC: {precision_recall_data[algo]['AUROC']:.4f}")

# Plot Precision-Recall curves
plt.figure(figsize=(10, 8))
colors = {
    "MV"      : "blue",
    "Hishi"   : "red",
    "RWR"     : "green",
    "FF"      : "purple",
    "Ensemble": "brown"
}

for algo, color in colors.items():
    precision_vals = precision_recall_data[algo]['precision']
    recall_vals    = precision_recall_data[algo]['recall']
    aupr           = precision_recall_data[algo]['AUPR']
    plt.plot(recall_vals, precision_vals,
             color=color, alpha=0.5,
             label=f'{algo} (AUPR={aupr:.3f})')

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curves')
plt.legend(loc='best')
plt.savefig('precision_recall_curves.png', dpi=300)
plt.show()

# Plot ROC curves
plt.figure(figsize=(10, 8))

for algo, color in colors.items():
    fpr_vals  = precision_recall_data[algo]['fpr']
    tpr_vals  = precision_recall_data[algo]['tpr']
    auroc     = precision_recall_data[algo]['AUROC']
    plt.plot(fpr_vals, tpr_vals,
             color=color, alpha=0.5,
             label=f'{algo} (AUROC={auroc:.3f})')

plt.plot([0, 1], [0, 1],
         color='gray', linestyle='--',
         label='Random Classifier')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves')
plt.legend(loc='best')
plt.savefig('roc_curves.png', dpi=300)
plt.show()
