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

def unblock_edge_candidate(G, st, F, k, u):
    print("UNBLOCK EDGE CANDIDATE",u)
    F_u = [F_i for F_i in F if u in F_i][0]
    subgraph = nx.subgraph(G,F_u)
    for v1, v2 in set(subgraph.edges()).difference(st.edges()):
        if st.degree(v1) >= k-1 or st.degree(v2) >= k-1:
            continue
        else:
            C = find_cycle(st,v1,v2)
            if u in C:
                st.add_edge(v1,v2)
                print("unblock add edge",v1,v2)
                neighbor_to_remove = set(C).intersection(set(st.neighbors(u))).pop()
                print("unblock remove edge",u,neighbor_to_remove)
                st.remove_edge(u, neighbor_to_remove)
                if not nx.is_connected(st):
                    import pdb
                    pdb.set_trace()
                break

def approximate_min_deg_st(G):
    print("original graph",list(G.edges()))
    st = nx.minimum_spanning_tree(G)
    print("spanning tree edges",list(st.edges()))
    while True:
        marks = dict({node:'good' for node in st.nodes})
        k = max(dict(st.degree).values())
        for node in st.nodes():
            if st.degree(node) >= k-1:
                marks[node] = 'bad'
        forest = nx.subgraph(st,[node for node in st.nodes if marks[node] == 'good'])
        F = list(nx.connected_components(forest))
        # print("connected components",F)
        k_candidate = None
        # print("bad nodes for k=",k,":",marks)
        print("degree dict",dict(st.degree))
        while all([True if marks[node] == 'bad' else False for node in st.nodes if st.degree(node) == k]):
            edge = get_edge_between_components(G,F)
            if not edge:
                break
            u,v = edge
            # st.add_edge(u,v)
            # print("add edge",u,v)
            C = find_cycle(st,u,v)
            if not C:
                import pdb
                pdb.set_trace()
            for node in C:
                if st.degree(node) >= k-1 and marks[node] == 'bad':
                    marks[node] = 'good'
                    if st.degree(node) == k:
                        #this is where we really find a candidate ending the while loop
                        k_candidate = (node, (u,v), C)
            forest = nx.subgraph(st,[node for node in st.nodes if marks[node] == 'good'])
            F = list(nx.connected_components(forest))
        
        if k_candidate:
            candidate, (u,v), circle = k_candidate
            if st.degree(u) >= k-1:
                # print("degree u",st.degree(u),"k",k)
                unblock_edge_candidate(G, st, F, k, u)
            
            if st.degree(v) >= k-1:
                # print("degree v",st.degree(v),"k",k)
                unblock_edge_candidate(G, st, F, k, v)
            
            print("reduce degree of vertex ",candidate,"with neighbors",list(st.neighbors(candidate)),"by introducing an edge on",u,v)
            st.add_edge(u,v)
            neighbor_to_remove = set(circle).intersection(set(st.neighbors(candidate))).pop()
            print("remove edge",candidate, neighbor_to_remove)
            st.remove_edge(candidate, neighbor_to_remove)
            if not nx.is_connected(st):
                import pdb
                pdb.set_trace()
            print("new spanning tree",list(st.edges()))
        else:
            break
    assert(nx.is_connected(st))
    assert(len(st.edges()) == len(st.nodes())-1)
    assert(all([True if edge in G.edges() else False for edge in st.edges()]))
    return st

if __name__ == "__main__":
    random.seed(1234)
    G = nx.erdos_renyi_graph(50,0.4)
    approximate_min_deg_st(G)