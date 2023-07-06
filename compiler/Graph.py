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

def create_tree_dfs(graph, head_value):
    visited = set()

    tree_head = TreeNode(head_value)
    t = Tree(tree_head)

    stack = []
    stack.append(tree_head)
    visited.add(tree_head.value)

    while stack:
        node = stack.pop()
        t.vertices.append(node)

        for n in graph.neighbors(node.value):
            if n not in visited:
                tree_n = TreeNode(n)
                tree_n.parent = node
                node.children.append(tree_n)

                visited.add(n)
                stack.append(tree_n)
    return t

def traverse_dfs(tree, head_node):
    visited = set()

    tree_head = TreeNode(head_node.value)
    t = Tree(tree_head)

    stack = []
    stack.append(head_node)
    visited.add(head_node.value)

    while stack:
        node = stack.pop()
        t.vertices.append(node)

        for n in node.neighbors():
            if n.value not in visited:
                tree_n = TreeNode(n.value)
                tree_n.parent = node
                node.children.append(tree_n)

                visited.add(n.value)
                stack.append(n)

    return t

def create_tree_bfs(graph, head_value):
    visited = set()

    tree_head = TreeNode(head_value)
    t = Tree(tree_head)

    queue = []
    queue.append(tree_head)
    visited.add(tree_head.value)

    while queue:
        node = queue.pop(0)
        t.vertices.append(node)

        for n in graph.neighbors(node.value):
            if n not in visited:
                tree_n = TreeNode(n)
                tree_n.parent = node
                node.children.append(tree_n)

                visited.add(n)
                queue.append(tree_n)
    return t

def py_tree(graph, tree):
    queue =[]
    queue.append(tree.head)
    while queue:
        node = queue.pop(0)
        for n in node.children:
            queue.append(n)
            graph.set_edge_type(graph.edge(n.value, node.value), 1)
        
class Tree:
    def __init__(self, head):
        self.head = head
        self.vertices = []

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

    def neighbors(self):
        if self.parent != None:
            return [self.parent] + self.children
        else:
            return self.children

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
