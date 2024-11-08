from compiler.QTree import create_tree_dfs, Tree, TreeNode, QTree, build_optimal, build_optimal_linear
from graphtheory.approximate_min_deg_st import approximate_min_deg_st
import networkx as nx
import random

## helper functions; TODO: fix graph structure, there should not be nx + pyzx graphs + Trees but just one format
def vdsp_to_nx(T):
    edge_list = []
    current = [T.head]
    while current:
        next = []
        for node in current:
            for child in node.children:
                edge_list.append((node.value,child.value))
                next.append(child)
        current = next
    return nx.Graph(edge_list)

def nx_to_vdsp(T: nx.Graph, head):
    head_node = TreeNode(head)
    vdsp_tree = Tree(head_node)
    current = [head_node.value]
    visited = [head_node.value]
    while current:
        next = []
        for node in current:
            for neighbor in T.neighbors(node):
                if not neighbor in visited:
                    visited.append(neighbor)
                    vdsp_tree.add_edge(node,neighbor)
                    next.append(neighbor)
        current = next
    return vdsp_tree

def min_degree_dfs(G: nx.Graph):
    T = dfs(G)
    return approximate_min_deg_st(G,T)

def dfs(G: nx.Graph):
    v = list(G.nodes)[0]
    return vdsp_to_nx(create_tree_dfs(G,v))

def longest_line_dfs(G: nx.Graph):
    longest_tree = (None,0)
    for v in list(G.nodes):
        T = create_tree_dfs(G,v)
        depth = T.depth()
        if depth > longest_tree[1]:
            longest_tree = (T,depth)
    return vdsp_to_nx(longest_tree[0])

def min_degree_longest_line(G: nx.Graph):
    T = longest_line_dfs(G)
    return approximate_min_deg_st(G,T)

def get_optimal_tree(g: nx.Graph, st_extraction_method = dfs):
    optimal_tree = None
    optimal_outer_loops = -1
    t = st_extraction_method(g)
    for head in t.nodes:
        vdsp_tree = nx_to_vdsp(t, head)
        q = QTree(head)
        print("before build optimal")
        build_optimal.counter = 0
        current_loops = build_optimal(vdsp_tree.head,q, fusion_method="type2")
        #    current_loops = build_optimal_linear(vdsp_tree.head,q, fusion_method="type2")
        print("build optimal was called ",build_optimal.counter,"times")
        print("current loops for head",head,current_loops)

        if optimal_outer_loops == -1 or current_loops < optimal_outer_loops:
            optimal_outer_loops = current_loops
            optimal_tree = t
    return (optimal_tree, optimal_outer_loops)

def compare_methods(G: nx.Graph):
    methods = {'min_degree': min_degree_dfs, 'dfs': dfs, 'longest_line': longest_line_dfs, 'min_degree_longest_line': min_degree_longest_line}
    for name, method in methods.items():
        optimum = get_optimal_tree(G, method)
        # import pdb
        # pdb.set_trace()
        print("num outer loops ",name,":",optimum[1])

if __name__ == "__main__":
    random.seed(2234)
    G = nx.erdos_renyi_graph(13,0.4)
    print("G with edges",G.edges)
    compare_methods(G)

