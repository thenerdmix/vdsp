import networkx as nx
import itertools
import random

def get_edge_between_components(G,F):
    for i,c1 in enumerate(F):
        print(i,c1)
        for c2 in list(F)[i:]:
            print(c2)
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

def unblock_edge_candidate(G, st, F, k, u):
    F_u = [F_i for F_i in F if u in F_i][0]
    subgraph = nx.subgraph(G,F_u)
    for v1, v2 in set(subgraph.edges()).difference(st.edges()):
        if st.degree(v1) >= k-1 or st.degree(v2) >= k-1:
            continue
        else:
            st.add_edge(v1,v2)
            C = find_cycle(st,v1,v2)
            if u in C:
                st.remove_edge(u, set(C).intersection(set(st.neighbors(u))).pop())
                break

def approximate_min_deg_st(G):
    st = nx.minimum_spanning_tree(G)
    while True:
        marks = dict({node:'good' for node in st.nodes})
        k = max(dict(st.degree).values())
        for node in st.nodes():
            if st.degree(node) >= k-1:
                marks[node] = 'bad'
        forest = nx.subgraph(st,[node for node in st.nodes if marks[node] == 'good'])
        F = nx.connected_components(forest)
        k_candidate = None
        print("bad nodes",marks)
        while all([True if marks[node] == 'bad' else False for node in st.nodes if st.degree(node) == k]):
            edge = get_edge_between_components(G,F)
            if not edge:
                break
            u,v = edge
            st.add_edge(u,v)
            C = find_cycle(st,u,v)
            for node in C:
                if st.degree(node) >= k-1 and marks[node] == 'bad':
                    marks[node] = 'good'
                    if st.degree(node) == k:
                        #this is where we really find a candidate ending the while loop
                        k_candidate = (k, (u,v), C)
            forest = nx.subgraph(st,[node for node in st.nodes if marks[node] == 'good'])
            F = nx.connected_components(forest)
        
        if k_candidate:
            k, (u,v), circle = k_candidate
            if st.degree(u) >= k-1:
                unblock_edge_candidate(G, st, F, k, u)
            
            if st.degree(v) >= k-1:
                unblock_edge_candidate(G, st, F, k, v)
            
            st.add_edge(u,v)
            st.remove_edge(k, set(circle).intersection(set(st.neighbors(k))).pop())
        else:
            break
    return st

if __name__ == "__main__":
    random.seed(1234)
    G = nx.erdos_renyi_graph(10,0.4)
    approximate_min_deg_st(G)