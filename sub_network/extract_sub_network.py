import os
import networkx as nx
import pandas as pd
import numpy as np
import community.community_louvain as community_louvain
from collections import defaultdict

# -------------------- Load Network --------------------
network_file = "../network/human_RA_network.gml"
full_net     = nx.read_gml(network_file)
print("Network loaded!")

# -------------------- Load Candidates --------------------
score_file = r"D:\abi\abi\pythonProject\Abi 2025\Research\network\network\scores_for_predictions.xlsx"
score_data = pd.read_excel(score_file)
candidates = score_data["Node"].tolist()

# -------------------- Load Seeds --------------------
seed_data = pd.read_excel("../seed_retrieving/processed_protein.xlsx")
seeds     = [s for s in seed_data["preferredName"] if s in full_net.nodes]

# -------------------- Build Subnetwork --------------------
threshold_total = 0.2209 * 4  # = 0.8836

top_candidates = score_data[
    score_data["Total Score"] >= threshold_total
]["Node"].tolist()

print(f"Candidates above threshold: {len(top_candidates)}")

nodes_to_include = seeds + top_candidates
subnet           = full_net.subgraph(nodes_to_include).copy()
print(f"Subnetwork nodes: {len(subnet.nodes)}, edges: {len(subnet.edges)}")

# -------------------- Louvain Community Detection --------------------
partitions = community_louvain.best_partition(subnet)

# group nodes by module — exactly like reference
result = defaultdict(list)
for key, val in sorted(partitions.items()):
    result[val].append(key)

# -------------------- Intra-module degree stats --------------------
avg      = {}
std      = {}
intra_deg = {}
string   = ""

for key, val in sorted(result.items()):
    string += "\n " + str(key) + ' : ' + str(val)
    interactions = []
    for node in val:
        module_neighbors = [m for m in subnet.neighbors(node) if m in val]
        intra_deg[node]  = len(module_neighbors)
        interactions.append(len(module_neighbors))
    avg[key] = np.mean(interactions)
    std[key] = np.std(interactions)

with open("human_RA_partitions.txt", "w") as f:
    f.write(string)

# -------------------- Identify Hubs — exactly like reference --------------------
z_tot = []
hubs  = ""

for node in partitions:
    module = partitions[node]
    subnet.nodes[node]["cluster"] = module
    pc = 0

    # z-score calculation
    if std[module] != 0:
        z = (intra_deg[node] - avg[module]) / std[module]
    else:
        z = 0
    z_tot.append(z)

    if z >= 0.9:
        degree    = subnet.degree(node)
        neighbors = list(subnet.neighbors(node))

        # group neighbors by module — exactly like reference
        neighbor_partitions = {key: partitions[key] for key in neighbors}
        neighbor_modules    = defaultdict(list)
        for key, val in sorted(neighbor_partitions.items()):
            neighbor_modules[val].append(key)

        # PC formula — exactly like reference
        for key, val in neighbor_modules.items():
            pc += (len(val) / degree) ** 2
        pc = 1 - pc

        if pc > 0.5:
            pc = 2
        else:
            pc = 1

        hubs += (f"\nNode: {node}\n{dict(neighbor_modules)}\n"
                 f"module: {module}\n"
                 f"modules connecting: {neighbor_modules.keys()}\n"
                 f"{pc}\n\n")
    else:
        pc = 0

    subnet.nodes[node]["pc"] = pc

with open("human_RA_hubs.txt", "w") as f:
    f.write(hubs)

# -------------------- 90th percentile boundary — from reference --------------------
boundary = np.percentile(z_tot, 90)
print(f"90th percentile z-score boundary: {boundary:.4f}")

# -------------------- Save Subnetwork --------------------
nx.write_gml(subnet, "human_RA_sub_network.gml")
print("Subnetwork saved to human_RA_sub_network.gml")

# Candidates above threshold: 209
# Subnetwork nodes: 342, edges: 7693
# 90th percentile z-score boundary: 1.2434
# Subnetwork saved to human_RA_sub_network.gml