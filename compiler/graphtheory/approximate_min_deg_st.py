import networkx as nx
import itertools
import random

def get_edge_between_components(G,F):
    for i,c1 in enumerate(F):
        for c2 in F[i+1:]:
            for u,v in itertools.product(c1,c2):
                if G.has_edge(u,v):
                    return (u,v)
    return None

def find_cycle(T, u, v):
    parentMap = dict()
    visited = [u]
    parentMap[u] = v
    queue = [neighbor for neighbor in T.neighbors(u) if neighbor != v]
    for neighbor in queue:
        parentMap[neighbor] = u

    while queue:
        node = queue.pop()
        visited.append(node)
        for neighbor in T.neighbors(node):
            if neighbor in visited:
                continue
            parentMap[neighbor] = node
            if neighbor == v:
                cycle = [v]
                backtrack_node = v
                while parentMap[backtrack_node] != v:
                    backtrack_node = parentMap[backtrack_node]
                    cycle.append(backtrack_node)
                return cycle
            else:
                queue.append(neighbor)

    return None    

"""
Thoughts: 
If we remove all vertices with degree k and(!) k-1 in the first place, do we already find the correct improvements in the inner while loop?
So we would not neet to "find" improvements afterwards but just apply the edge additions found in the inner while loop and delete some adjacent edges
Can we remove any edge or does edge removal for a k-1 vertex lead to cycle breaking for the k vertex?
Edge addition and removal inside a component preserves connectedness, therefore we always get a cycle when connecting two other components afterwards?
"""

def approximate_min_deg_st(G, T=None):
    if not T:
        T = nx.minimum_spanning_tree(G)
    while True: 
        k = max(dict(T.degree).values())
        marks = dict({node:'good' if T.degree(node) < k-1 else 'bad' for node in T.nodes})
        forest = nx.subgraph(T,[node for node in T.nodes if marks[node] == 'good'])
        F = list(nx.connected_components(forest))
        edges_to_apply = dict()
        while True:
            edge = get_edge_between_components(G,F)
            if not (edge and all([True if marks[node] == 'bad' else False for node in T.nodes if T.degree(node) == k])):
                break
            u,v = edge
            C = find_cycle(T, u, v)
            for node in C:
                if marks[node] == 'bad':
                    marks[node] = 'good'
                    edges_to_apply[node] = (u,v)
            forest = nx.subgraph(T,[node for node in T.nodes if marks[node] == 'good'])
            F = list(nx.connected_components(forest))

        good_k_vertices = [node for node in T.nodes if marks[node] == 'good' and T.degree(node) == k]
        if good_k_vertices:
            k_vertex = good_k_vertices[0]
            u,v = edges_to_apply[k_vertex]
            if T.degree(u) == k-1:
                uu, uv = edges_to_apply[u]
                C = find_cycle(T, uu, uv)
                T.add_edge(uu, uv)
                T.remove_edge(u, set(C).intersection(set(T.neighbors(u))).pop())
            if T.degree(v) == k-1:
                vu, vv = edges_to_apply[v]
                C = find_cycle(T, vu, vv)
                T.add_edge(vu, vv)
                T.remove_edge(v, set(C).intersection(set(T.neighbors(v))).pop())
            
            C = find_cycle(T, u,v)
            T.add_edge(u,v)
            T.remove_edge(k_vertex, set(C).intersection(set(T.neighbors(k_vertex))).pop())
        else:
            break
        assert(nx.is_connected(T))
        assert(len(T.edges()) == len(T.nodes())-1)
        assert(all([True if edge in G.edges() else False for edge in T.edges()]))
    return T

if __name__ == "__main__":
    random.seed(1234)
    G = nx.erdos_renyi_graph(50,0.4)
    approximate_min_deg_st(G)