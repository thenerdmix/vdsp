from QTree import QTree, build_optimal
from Graph import Tree, TreeNode
import json
import sys

"""Reads in tree from json format file and outputs the number of outer loops"""

def read_in_tree(file):
    with open(file) as json_file:
        tree_dict = json.load(json_file)
        nodes = [TreeNode(i) for i in range(0,len(tree_dict.keys()))]
        t = Tree(nodes[0])
        for i in range(0,len(tree_dict.keys())):
            nodes[i].children = [nodes[j] for j in tree_dict[str(i)] if j > i]
        return t

if __name__ == "__main__":
    file = sys.argv[1]
    t = read_in_tree(file)
    q = QTree(t.head.value)
    current_loops = build_optimal(t.head,q)
    print(file,"has number of outer loops",current_loops)