import sys
sys.path.append('..')

from compiler.graphtheory.edge_optimize import find_maximal_independent_set, lcomp_edge_optimize_greedy
from compiler.QTree import create_tree_dfs, build_optimal, QTree
from pyzx.graph.base import BaseGraph, VT, ET
from pyzx import Graph
from pyzx.utils import EdgeType, VertexType
import networkx as nx
import random
import json


def create_random_graph(num_vertices, edge_prob):
    random_graph = nx.erdos_renyi_graph(num_vertices,edge_prob)
    g = Graph()
    vertex_dict = {v: g.add_vertex(VertexType.Z,random.random()*num_vertices/2,random.random()*num_vertices/2) for v in list(random_graph.nodes) if random_graph.degree(v) > 0}
    for u,v, _ in random_graph.edges.data():
        g.add_edge(g.edge(vertex_dict[u],vertex_dict[v]), EdgeType.HADAMARD)
    g.normalize()
    return g

def minimize_edges(g: BaseGraph[VT,ET]):
    independent_set = find_maximal_independent_set(g)
    lcomp_edge_optimize_greedy(g, independent_set)

def dump_tree(tree, filename):
    tree_dict = dict()
    for v in tree.vertices:
        neighbors = v.children + [v.parent]
        tree_dict[v.value] = [neighbor.value for neighbor in neighbors if neighbor]
    print(tree_dict)
    with open(filename, 'w') as f:
        json.dump(tree_dict, f)

def get_optimal_tree(g: BaseGraph[VT,ET]):
    optimal_tree = None
    optimal_outer_loops = -1
    for v in g.vertices():
        t = create_tree_dfs(g, list(g.vertices())[v])
        q = QTree(t.head.value)
        current_loops = build_optimal(t.head,q)
        if optimal_outer_loops == -1 or current_loops < optimal_outer_loops:
            optimal_outer_loops = current_loops
            optimal_tree = t
    return (optimal_tree, optimal_outer_loops)

if __name__ == "__main__":
    g = create_random_graph(12,0.4)
    print("original graph with",g.num_edges(),"edges")
    minimize_edges(g)
    print("after edge minimzer",g.num_edges(),"edges")
    optimal_tree, num_outer_loops = get_optimal_tree(g)
    print("partition into tree with",len(optimal_tree.vertices)-1,"edges and remaining graph with",g.num_edges()-len(optimal_tree.vertices)+1,"edges")
    print("tree has max degree of",max(map(lambda x: len(x.children)+1 if x != optimal_tree.head else len(x.children), optimal_tree.vertices)))
    print("tree has number of outer loops",num_outer_loops)
    dump_tree(optimal_tree, 'tree.json')