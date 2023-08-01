import pyzx as zx
import random

def to_graph_like(g):
    """Puts a generic ZX-graph into a ZX graph-like diagram.

    :param g: a generic ZX-graph
    :type g: BaseGraph
    """
    zx.spider_simp(g)
    zx.to_gh(g)
    zx.id_simp(g)
    zx.spider_simp(g)

def optimize_graph(g):
    """Simplify clifford spiders

    :param g: a generic ZX-graph
    :type g: BaseGraph
    """
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
    """Given a tree and a starting node, returns the new tree given by a DFS starting from head_node.

    :param tree: the tree to traverse
    :type tree: Tree
    :param head_node: the starting node
    :type head_node: TreeNode
    :return: the tree
    :rtype: the traversed tree
    """
    visited = set()

    tree_head = TreeNode(head_node.value)
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
                node.children.append(tree_n)

                visited.add(n.value)

                stack.append(n)
                stack_new.append(tree_n)

    return t


def py_tree(graph, tree):
    """Given a ZX-graph and a tree, it visualize the tree on the graph changing the color of the edges corresponding to the tree.

    :param graph: the ZX-graph on which we want to visualize the tree
    :type graph: BaseGraph
    :param tree: the tree
    :type tree: Tree
    """
    queue =[]
    queue.append(tree.head)
    while queue:
        node = queue.pop(0)
        for n in node.children:
            queue.append(n)
            graph.set_edge_type(graph.edge(n.value, node.value), 1)
        
class Tree:
    """A class to manage trees
    :param head: the head of the tree
    :type head: TreeNode
    :param vertices: the list of vertices belonging to the tree
    :type vertices: list of TreeNode objects
    """
    def __init__(self, head):
        """Constructor method
        """
        self.head = head
        self.vertices = []

    def add_edge(self, parent, children):
        """Add an edge to the tree. The parent vertex must be already present in the tree. The children vertex is a newly created TreeNode.

        :param parent: the parent node id
        :type parent: int
        :param children: the children node id
        :type children: int
        """
        parent_node = None
        for v in self.vertices:
            if v.value == parent:
                parent_node = v

        assert parent_node in self.vertices, print("The parent is not present in the tree")
        child_node = TreeNode(children)
        child_node.parent = parent_node
        parent_node.children.append(child_node)

        self.vertices.append(child_node)

class TreeNode:
    """A tree node.

    :param value: id of the node
    :type value: int
    :param parent: parent node
    :type parent: TreeNode
    :param children: list of children of the node
    :type children: list of TreeNode objects
    """
    def __init__(self, value):
        """Constructor method.
        """
        self.value = value
        self.parent = None
        self.children = []

    def neighbors(self):
        """Returns all the neighbors of a tree node: parent and children.

        :return: neighbors of a tree node
        :rtype: list of TreeNode objects
        """
        if self.parent != None:
            return [self.parent] + self.children
        else:
            return self.children

def random_tree(size):
    """Generate a random tree.

    :param size: number of vertices of the random tree.
    :type size: int
    :return: random tree
    :rtype: Tree
    """
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
    """Recursively computes an upper bound for the number of outer loops needed to implement the subtree with head node start

    :param tree: the starting tree to bound
    :type tree: Tree
    :param start: the head node of the subtree to bound
    :type start: TreeNode
    :param bound_list: the list to fill with the bounds
    :type bound_list: list
    :return: bound for the start node
    :rtype: int
    """
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

class Graph:
    """A general ZX-graph.

    :param original_graph: the original ZX-graph
    :type original_graph: BaseGraph
    :param graph: the ZX-graph without inputs and outputs vertices.
    :type graph: BaseGraph
    """
    def __init__(self):
        """Constructor method.
        """
        self.original_graph = None
        self.graph = None

    def construct_from_json(self, graph_json):
        """Generate the ZX graph-like diagram from a json. It also optimize it.

        :param graph_json: the json describing the ZX-graph
        :type graph_json: str
        """
        g = zx.Graph.from_json(graph_json)
        to_graph_like(g)
        optimize_graph(g)
        g.normalize()

        self.original_graph=g

        g = g.copy()
        g.remove_vertices(g.inputs()+g.outputs())

        self.graph = g.copy()