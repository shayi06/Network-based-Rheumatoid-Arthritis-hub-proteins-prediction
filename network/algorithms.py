import networkx as nx
import numpy as np
import pandas as pd
from scipy import sparse


def _array_initiation_(graph, seeds):
    degree_matrix    = np.zeros((len(graph.nodes), 1))
    remaining_fluid  = np.zeros((len(graph.nodes), 1))
    entered_fluid    = np.zeros((len(graph.nodes), 1))

    i = 0
    for name in graph.nodes:
        degree_matrix[i, 0] = 1 / (graph.degree(name, "weight"))
        if name in seeds:
            remaining_fluid[i, 0] = float("inf")
            entered_fluid[i, 0]   = float("inf")
        i += 1

    adj_matrix = nx.adjacency_matrix(graph)
    adj_matrix = sparse.csr_matrix(adj_matrix.toarray())

    return [adj_matrix, degree_matrix, entered_fluid, remaining_fluid]


def score_calculation(sign1, sign_list1, deg1, clue1,
                      sign2, sign_list2, deg2, clue2, max_rem_fluid):
    res = []
    for s, l, d, t in zip(
        (sign1, sign2),
        (sign_list1, sign_list2),
        (deg1, deg2),
        (clue1, clue2)
    ):
        updated_deg_matrix       = sparse.csr_matrix.multiply(s, d)
        weight_proportion        = sparse.csr_matrix.multiply(l, updated_deg_matrix)
        reservoir_cap            = sparse.csr_matrix.multiply(s, max_rem_fluid)
        using_remainder_weights  = sparse.csr_matrix.multiply(weight_proportion, reservoir_cap)

        if t == "p":
            fluid_volume = sparse.csr_matrix.minimum(l, using_remainder_weights)
        elif t == "n":
            fluid_volume = sparse.csr_matrix.maximum(l, using_remainder_weights)

        res.append(fluid_volume)
    return res


def functional_flow(graph, seeds, d):
    arrays = _array_initiation_(graph, seeds)

    for i in range(0, d):
        t_rem_fluid   = arrays[3].transpose()
        mesh_rem_fluid = np.meshgrid(arrays[3], t_rem_fluid)
        max_rem_fluid  = np.maximum(*mesh_rem_fluid)

        greater = np.greater(t_rem_fluid, arrays[3])
        greater = sparse.csr_matrix(greater * 1)

        less = np.less(t_rem_fluid, arrays[3])
        less = sparse.csr_matrix(less * -1)

        positives = sparse.csr_matrix.multiply(greater, arrays[0])
        negatives = sparse.csr_matrix.multiply(less,    arrays[0])

        n = negatives.copy()
        p = positives.copy()
        n[n < 0] = 1
        p[p > 0] = 1

        result = score_calculation(
            p, positives, arrays[1].transpose(), "p",
            n, negatives, arrays[1],              "n",
            max_rem_fluid
        )

        entered_fluid = sparse.csr_matrix.sum(result[0], axis=1)
        fluid_exit    = sparse.csr_matrix.sum(result[1], axis=1)
        update_rem    = np.add(entered_fluid, fluid_exit)

        arrays[3] = np.add(arrays[3], update_rem)
        arrays[2] = np.add(arrays[2], entered_fluid)

    x = 0
    for node in graph.nodes:
        graph.nodes[node]['functional_score'] = arrays[2][x, 0]
        x += 1

    return graph


def predict(graph, seeds, d):
    functional_flow(graph, seeds, d)

    import network_prop
    network_prop.netprop(graph, seeds, 100, 0.1, 5)

    scores = pd.DataFrame()

    for node in graph.nodes:
        if node not in seeds:
            rwr = graph.nodes[node]['propagated_weight']
            fun = graph.nodes[node]['functional_score']

            li    = [m for m in graph.neighbors(node)]
            known = [x for x in li if x in seeds]
            ef    = (len(seeds) * len(li) / len(graph.nodes))
            nf    = len(known)

            if nf != 0:
                hishigaki = (nf - ef) ** 2 / ef
            else:
                hishigaki = 0

            mv  = len(known)
            row = {
                "Node"                  : node,
                "Majority voting score" : mv,
                "Hishigaki score"       : hishigaki,
                "Functional flow score" : fun,
                "RWR"                   : rwr
            }
            scores = scores._append(row, ignore_index=True)

    # Normalize
    minrwr  = min(scores["RWR"])
    maxrwr  = max(scores["RWR"])
    minfun  = min(scores["Functional flow score"])
    maxfun  = max(scores["Functional flow score"])
    minmv   = min(scores["Majority voting score"])
    maxmv   = max(scores["Majority voting score"])
    minh    = min(scores["Hishigaki score"])
    maxh    = max(scores["Hishigaki score"])

    for index, row in scores.iterrows():
        rwr   = (row["RWR"] - minrwr)                           / (maxrwr - minrwr)
        funsc = (row["Functional flow score"] - minfun)         / (maxfun - minfun)
        mvsc  = (row["Majority voting score"] - minmv)          / (maxmv  - minmv)
        hsc   = (row["Hishigaki score"] - minh)                 / (maxh   - minh)
        tot   = rwr + funsc + mvsc + hsc

        scores.at[index, "Normalized majority voting score"] = mvsc
        scores.at[index, "Normalized hishigaki score"]       = hsc
        scores.at[index, "Normalized functional flow score"] = funsc
        scores.at[index, "Normalized rwr score"]             = rwr
        scores.at[index, "Total Score"]                      = tot

    sorted_scores = scores.sort_values("Total Score", ascending=False)
    sorted_scores.to_excel("scores_for_predictions.xlsx")
    print("✅ Prediction scores saved to scores_for_predictions.xlsx")
    print(f"Top prediction: {sorted_scores.iloc[0]['Node']}")