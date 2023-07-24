from Graph import *
from QTree import *

t = random_tree(20)

#head = TreeNode(0)
#t = Tree(head)
#t.vertices.append(head)
#
#t.add_edge(0, 1)
#t.add_edge(1, 2)
#t.add_edge(0, 3)
#t.add_edge(3, 4)
#t.add_edge(0, 5)
#t.add_edge(1, 6)
#t.add_edge(2, 7)
#t.add_edge(5, 8)
#t.add_edge(4, 9)
#

print([v.value for v in t.vertices])
print([v.offspring for v in t.vertices])
print([weight(t, v, reverse=True) for v in t.vertices])


order = [0]
depth = [1]

q = QTree(head_id = 0)
for i in range(1, len(t.vertices)):
    q.add_overall(t.vertices[i].parent.value, t.vertices[i].value, order, depth)

print(max(depth))

##########################

t = traverse_dfs(t, t.head)
t.order_by_weight(reverse=False)
t = traverse_dfs(t, t.head)

print([v.value for v in t.vertices])
print([v.offspring for v in t.vertices])
print([weight(t, v, reverse=True) for v in t.vertices])

bound_list = [None]*len(t.vertices)
bound_tree(t, t.head, bound_list)

order = [0]
depth = [1]

q = QTree(head_id = 0)
for i in range(1, len(t.vertices)):
    q.add_overall(t.vertices[i].parent.value, t.vertices[i].value, order, depth)

print([bound_list[i] for i in order])

print(max(bound_list))
print(max(depth))

#q.loop.loopify()
#pcvl.pdisplay(q.loop.circuit)

########################################

t = traverse_dfs(t, t.head)
t.order_by_weight(reverse=True)
t = traverse_dfs(t, t.head)

print([v.value for v in t.vertices])
print([v.offspring for v in t.vertices])
print([weight(t, v, reverse=True) for v in t.vertices])

bound_list = [None]*len(t.vertices)
bound_tree(t, t.head, bound_list)

order = [0]
depth = [1]

q = QTree(head_id = 0)
for i in range(1, len(t.vertices)):
    q.add_overall(t.vertices[i].parent.value, t.vertices[i].value, order, depth)

print([bound_list[i] for i in order])

print(max(bound_list))
print(max(depth))

#q.loop.loopify()
#pcvl.pdisplay(q.loop.circuit)

e = -1
d = -1
for v in t.vertices:
    e = max(e, len(v.children))
    d = max(d, v.depth)

print(3*(e-1)*d + 3)


