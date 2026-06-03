import json
import numpy as np


# function for min-max normalization
def min_max_normalize(array, num):
    min_val = np.min(array)
    max_val = np.max(array)

    if max_val == min_val:
        return num

    return (num - min_val) / (max_val - min_val)

with open(r'D:\abi\abi\pythonProject\Abi 2025\Research\network\network\all_scores.json', 'r') as file:
    data = json.load(file)

algos = ['MV', 'Hishi', 'RWR', 'FF']

# exactly like repo
# global storage — NOT per fold
algo_scores = {
    'MV'      : {},
    'Hishi'   : {},
    'RWR'     : {},
    'FF'      : {},
    'Ensemble': {}
}

dep = {}
norm_dep = {}

# combine ALL folds together
# then normalize globally
for i in range(1, 11):
    fold_str = str(i)
    proteins = list(data[fold_str]['MV'].keys())

    for protein in proteins:
        dep_score = 0
        for algo in algos:
            dep_score += data[fold_str][algo][protein]

        # no DEPs in your case
        # original adds +1 if protein in DEPs
        # we skip that

        dep[protein] = dep_score

# normalize ensemble globally
for protein, score in dep.items():
    dep_values         = list(dep.values())
    norm_dep[protein]  = min_max_normalize(dep_values, score)

# store normalized scores
for i in range(1, 11):
    fold_str = str(i)
    for algo in algos:
        for protein in data[fold_str][algo].keys():
            algo_scores[algo][protein]     = data[fold_str][algo][protein]
            algo_scores['Ensemble'][protein] = norm_dep[protein]

# save
with open('algo_scores.json', 'w') as file:
    json.dump(algo_scores, file, indent=4)

print(f"✅ algo_scores.json saved!")
print(f"Total proteins: {len(algo_scores['MV'])}")
