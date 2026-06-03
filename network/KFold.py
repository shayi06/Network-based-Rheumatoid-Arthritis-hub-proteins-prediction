import networkx as nx
import pandas as pd
import json
from sklearn.model_selection import KFold
import network_prop
import algorithms


def MV_and_Hishi_score(nodes, graph, seeds):
    for node in nodes:
        neighbors    = list(graph.neighbors(node))
        seed_neighbors = sum(1 for n in neighbors if n in seeds)
        graph.nodes[node]["MV"] = seed_neighbors
        ef = (len(seeds) * len(neighbors) / len(graph.nodes))
        nf = seed_neighbors
        if nf != 0:
            graph.nodes[node]["Hishi"] = (nf - ef) ** 2 / ef
        else:
            graph.nodes[node]["Hishi"] = 0


def k_fold_cross_validation(graph, seeds_nodes, k):
    kf          = KFold(n_splits=k, shuffle=True, random_state=42)
    seed_splits = list(kf.split(seeds_nodes))
    all_scores  = {i: {} for i in range(1, k + 1)}
    count       = 0

    for train_indices, test_indices in seed_splits:
        count += 1

        train_nodes  = [seeds_nodes[i] for i in train_indices]
        train_seeds  = list(set(train_nodes) & set(seeds))
        all_scores[count]["train_seeds"] = train_seeds

        test_nodes = [seeds_nodes[i] for i in test_indices]
        all_scores[count]["test_seeds"] = list(set(test_nodes) & set(seeds))

        print(f"\n=== Fold {count} ===")
        print(f"Train seeds: {len(train_seeds)}")
        print(f"Test seeds:  {len(all_scores[count]['test_seeds'])}")
        print(f"Test nodes:  {len(test_nodes)}")

        MV_and_Hishi_score(test_nodes, graph, train_seeds)
        network_prop.netprop(graph, train_seeds, 100, 0.1, 5)
        algorithms.functional_flow(graph, train_seeds, 5)

        all_scores[count]["MV"]    = {}
        all_scores[count]["Hishi"] = {}
        all_scores[count]["RWR"]   = {}
        all_scores[count]["FF"]    = {}

        for node in test_nodes:
            all_scores[count]["MV"][node]    = graph.nodes[node]["MV"]
            all_scores[count]["Hishi"][node] = graph.nodes[node]["Hishi"]
            all_scores[count]["RWR"][node]   = graph.nodes[node]['propagated_weight']
            all_scores[count]["FF"][node]    = graph.nodes[node]['functional_score']

    with open("all_scores.json", 'w') as f:
        json.dump(all_scores, f, indent=4)
    print("\n✅ all_scores.json saved!")


# -------------------- Main --------------------
graph = nx.read_gml("human_RA_network.gml")

data  = pd.read_excel(r"D:\abi\abi\pythonProject\Abi 2025\Research\network\seed_retrieving\processed_protein.xlsx")
seeds = [m for m in data["preferredName"]]
seeds = [s for s in seeds if s in graph.nodes]

seeds_nodes = seeds + list(graph.nodes)
seeds_nodes = list(set(seeds_nodes))

print(f"Number of seeds: {len(seeds)}")
print(f"Number of seeds and nodes: {len(seeds_nodes)}")

k_fold_cross_validation(graph, seeds_nodes, k=10)