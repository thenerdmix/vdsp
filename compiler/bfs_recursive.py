from Graph import *
from QTree import *

#t = random_tree(30)


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
print(build_optimal(t.head, q))

for v in q.qvertices:
    print("optimal add, adding vertex ", v)
    print(q.depth_analysis()[v])

for v in t.vertices:
    print(v.value, build_optimal(v, QTree(v.value)))



#q.loop.loopify()
#pcvl.pdisplay(q.loop.circuit)

