import networkx as nx
import numpy as np

scale_limit = 100.0


def weights_from_seeds(graph, seedlist, weight=100):
    p0 = []
    seeds = seedlist
    for name in graph.nodes:
        if name in seeds:
            p0.append(weight)
        else:
            p0.append(0)
    p0 = np.array(p0)
    return p0


def _rwr(p0, alpha, A, invD, iter):
    invD = np.array(invD)
    cA   = np.array(A.toarray())
    W    = np.matmul(cA, invD)

    alp0 = np.array(alpha * p0)
    p    = alp0
    for i in range(iter):
        p = alp0 + (1 - alpha) * np.dot(W, p)
    return p


def graph_with_weights(wgraph, p, scale=True):
    if scale:
        p *= scale_limit / p.max()
    i = 0
    for node in wgraph.nodes:
        wgraph.nodes[node]['propagated_weight'] = p[i]
        i += 1
    return wgraph


def netprop(graph, seedlist, weight, alpha, iter, scale=True):
    A = nx.adjacency_matrix(graph)

    D    = np.eye(graph.number_of_nodes())
    i    = 0
    for name, degree in graph.degree:
        D[i, i] = degree
        i += 1
    invD = np.linalg.inv(D)

    p0 = weights_from_seeds(graph, seedlist, weight)
    p  = _rwr(p0, alpha, A, invD, iter)
    graph_with_weights(graph, p, scale)