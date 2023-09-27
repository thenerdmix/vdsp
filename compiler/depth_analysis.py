from Graph import *
from QTree import *

#####RANDOM#####
print("RANDOM ORDER")
head = TreeNode(0)
t = Tree(head)
t.vertices.append(head)

t.add_edge(0, 1)
t.add_edge(0, 2)
t.add_edge(1, 3)
t.add_edge(1, 4)
t.add_edge(0, 5)
t.add_edge(1, 6)
t.add_edge(1, 7)
t.add_edge(0, 8)
t.add_edge(6, 9)
t.add_edge(5, 10)
t.add_edge(3, 11)
t.add_edge(0, 12)
t.add_edge(7, 13)
t.add_edge(1, 14)
t.add_edge(5, 15)
t.add_edge(4, 16)
t.add_edge(7, 17)
t.add_edge(7, 18)
t.add_edge(16, 19)

q = QTree(t.head.value)
order = [t.head.value]
depth = [1]

for i in range(1, len(t.vertices)):
    print("child:", t.vertices[i].value, "parent:", t.vertices[i].parent.value)
    q.add_edge(t.vertices[i].parent.value, t.vertices[i].value)
    q.add_simul(t.vertices[i].parent.value, t.vertices[i].value, order, depth)

#####OPTIMAL BFS#####
print("OPTIMAL BFS")
head = TreeNode(0)
t = Tree(head)
t.vertices.append(head)

t.add_edge(0, 12)
t.add_edge(0, 8)
t.add_edge(0, 2)
t.add_edge(0, 5)
t.add_edge(5, 15)
t.add_edge(5, 10)
t.add_edge(0, 1)
t.add_edge(1, 14)
t.add_edge(1, 6)
t.add_edge(6, 9)
t.add_edge(1, 4)
t.add_edge(4, 16)
t.add_edge(16, 19)
t.add_edge(1, 3)
t.add_edge(3, 11)
t.add_edge(1, 7)
t.add_edge(7, 18)
t.add_edge(7, 17)
t.add_edge(7, 13)

q = QTree(t.head.value)
order = [t.head.value]
depth = [1]

for i in range(1, len(t.vertices)):
    print("child:", t.vertices[i].value, "parent:", t.vertices[i].parent.value)
    q.add_edge(t.vertices[i].parent.value, t.vertices[i].value)
    q.add_simul(t.vertices[i].parent.value, t.vertices[i].value, order, depth)

#####WORST BFS#####
print("WORST BFS")
head = TreeNode(0)
t = Tree(head)
t.vertices.append(head)

t.add_edge(0, 1)
t.add_edge(1, 7)
t.add_edge(7, 13)
t.add_edge(7, 17)
t.add_edge(7, 18)
t.add_edge(1, 3)
t.add_edge(3, 11)
t.add_edge(1, 4)
t.add_edge(4, 16)
t.add_edge(16, 19)
t.add_edge(1, 6)
t.add_edge(6, 9)
t.add_edge(1, 14)
t.add_edge(0, 5)
t.add_edge(5, 10)
t.add_edge(5, 15)
t.add_edge(0, 2)
t.add_edge(0, 8)
t.add_edge(0, 12)

q = QTree(t.head.value)
order = [t.head.value]
depth = [1]

for i in range(1, len(t.vertices)):
    print("child:", t.vertices[i].value, "parent:", t.vertices[i].parent.value)
    q.add_edge(t.vertices[i].parent.value, t.vertices[i].value)
    q.add_simul(t.vertices[i].parent.value, t.vertices[i].value, order, depth)