import networkx as nx
import pandas as pd
import os
import algorithms

# -------------------- Load Seeds --------------------
data = pd.read_excel(r"D:\abi\abi\pythonProject\Abi 2025\Research\network\seed_retrieving\processed_protein.xlsx")
seeds = [m for m in data["preferredName"]]

# -------------------- Build Network --------------------
if os.path.exists("human_RA_network.gml"):
    human_net = nx.read_gml("human_RA_network.gml")
else:
    protein_map = {}
    info = pd.read_table("../9606.protein.info.v12.0.txt", sep="\t", low_memory=False)
    for i, row in info.iterrows():
        protein_map[row['#string_protein_id']] = row['preferred_name']

    links = pd.read_table("../9606.protein.links.v12.0.txt", sep=' ')
    links = links.drop_duplicates()

    G = nx.Graph()
    for index, row in links.iterrows():
        p1 = row["protein1"]
        p2 = row["protein2"]
        pr1 = protein_map.get(p1)
        pr2 = protein_map.get(p2)
        if not pr1 or not pr2:
            continue
        sc = row["combined_score"] / 1000
        if sc >= 0.7:   # 0.7 for human (high confidence)
            G.add_edge(pr1, pr2, weight=sc)

    human_net = nx.Graph()
    if not nx.is_connected(G):
        largest_cc = max(nx.connected_components(G), key=len)
        human_net = G.subgraph(largest_cc).copy()
    else:
        human_net = G

    for node in human_net.nodes:
        human_net.nodes[node]["seeds"] = 1 if node in seeds else 0

    nx.write_gml(human_net, "human_RA_network.gml")

# -------------------- Predict --------------------
known_in = [s for s in seeds if s in human_net.nodes]
print("Seeds in network:", len(known_in))

d = 5
algorithms.predict(human_net, known_in, d)