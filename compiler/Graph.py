import pyzx as zx
import random
from QTree import *

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

def calc_offspring(head):
    for c in head.children:
        calc_offspring(c)
        head.offspring+= c.offspring+1

def traverse_dfs(tree, head_node):
    visited = set()

    tree_head = TreeNode(head_node.value)
    tree_head.depth = 0
    t = Tree(tree_head)

    stack = []
    stack_new = []

    stack.append(head_node)
    stack_new.append(tree_head)
    visited.add(head_node.value)

    while stack:
        node = stack_new.pop()
        t.vertices.append(node)

        s = stack.pop()
        for n in s.neighbors():
            if n.value not in visited:
                tree_n = TreeNode(n.value)
                tree_n.parent = node
                tree_n.depth = tree_n.parent.depth+1
                node.children.append(tree_n)

                visited.add(n.value)

                stack.append(n)
                stack_new.append(tree_n)


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

    def add_edge(self, parent, children):
        parent_node = None
        for v in self.vertices:
            if v.value == parent:
                parent_node = v

        assert parent_node in self.vertices, print("The parent is not present in the tree")
        child_node = TreeNode(children)
        child_node.parent = parent_node
        parent_node.children.append(child_node)

        self.vertices.append(child_node)

    def order_by_offspring(self):
        for v in self.vertices:
            v.children.sort(key=lambda x: x.offspring, reverse=False)

    def order_by_weight(self, reverse=True):
        for v in self.vertices:
            v.children.sort(key=lambda x: weight(self, x, reverse=reverse), reverse=reverse)

    def get_node(self, value):
        for v in self.vertices:
            if v.value == value:
                return v 
        return None

    

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []
        self.offspring = 0
        self.depth = None

    def neighbors(self):
        if self.parent != None:
            return [self.parent] + self.children
        else:
            return self.children

def random_tree(size):
    head_node = TreeNode(0)
    tree = Tree(head_node)
    tree.vertices.append(head_node)
    for i in range(1, size):
        parent_node = random.choice(tree.vertices)
        print(parent_node.value, i)
        child_node = TreeNode(i)
        parent_node.children += [child_node]
        child_node.parent = parent_node
        tree.vertices.append(child_node)

    return tree


def bound_tree(tree, start, bound_list):
    if not start.children:
        bound_list[start.value] = 3
        return 3
    i = 0
    m = -1
    for c in start.children:
        m = max(m, bound_tree(tree, c, bound_list)+3*i)
        i+=1
    
    bound_list[start.value] = m
    return m

def weight(tree, start, reverse):
    if not start.children:
        return 3
    m = -1
    sons = []
    for c in start.children:
        sons.append(weight(tree, c, reverse=reverse))

    sons.sort(reverse=reverse)
    for i in range(len(sons)):
        sons[i]+=3*i
    
    return max(sons)

def build_optimal(node, qtree):
    node.children.sort(key=lambda x: build_optimal(x, QTree(head_id = x.value)), reverse=False)
    for c in node.children:
        qtree.add_edge(node.value, c.value)
        build_optimal(c, qtree)
    return max(qtree.depth_analysis().values())

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
