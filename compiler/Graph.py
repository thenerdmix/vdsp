import pyzx as zx

def to_graph_like(g):
    zx.spider_simp(g)
    zx.to_gh(g)
    zx.id_simp(g)
    zx.spider_simp(g)

def optimize_graph(g):
    zx.simplify.clifford_simp(g)
    zx.full_reduce(g)
    zx.simplify.interior_clifford_simp(g)

def create_tree(graph, head_value):
    visited = set()

    tree_head = TreeNode(head_value)
    t = Tree(tree_head)
    t.pyg = graph.copy()

    recursive_dfs(graph, tree_head, t, visited)

    return t


def recursive_dfs(graph, node, tree, visited):
    visited.add(node.value)

    tree.vertices.append(node)            

    for n in graph.neighbors(node.value):
        if n not in visited:

            tree_n = TreeNode(n)
            tree_n.parent = node
            node.children.append(tree_n)

            tree.pyg.set_edge_type(tree.pyg.edge(n, node.value), 1)
            print()

            recursive_dfs(graph, tree_n, tree, visited)
        
class Tree:
    def __init__(self, head):
        self.head = head
        self.vertices = []
        self.pyg = None

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

        self.pyv = None

class Graph:

    def __init__(self, graph_json):
        g = zx.Graph.from_json(graph_json)
        to_graph_like(g)
        optimize_graph(g)
        g.normalize()

        self.original_graph=g

        g = g.copy()
        g.remove_vertices(g.inputs()+g.outputs())

        self.graph = g.copy()
