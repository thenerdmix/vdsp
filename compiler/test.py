from Graph import *
from Loop import *
from QTree import *

from qiskit import transpile, QuantumCircuit
import perceval as pcvl

import random

#circuit='./circuits/grover-orig.qasm'
#circuit='./circuits/grover.qasm'
#circuit='./circuits/vbe_adder_3.qasm'
#circuit='QASMBench/small/linearsolver_n3/linearsolver_n3.qasm'
#circuit='QASMBench/small/qaoa_n3/qaoa_n3.qasm'
circuit='QASMBench/small/bell_n4/bell_n4.qasm'
#circuit='./circuits/grover-2.qasm'
#circuit='QASMBench/small/qaoa_n3/qaoa_n3.qasm'

qc = QuantumCircuit.from_qasm_file(circuit)
qc = transpile(qc, basis_gates=['id','cx', 'cz', 'rz', 'h'])
c = zx.Circuit.from_qasm(qc.qasm()).to_graph()

p = Graph(c.to_json())

tree = create_tree_bfs(p.graph, list(p.graph.vertices())[0])

q = QTree(head_id=0)

order = [0]
depth = [1]


N = 50
for i in range(1, N):
    if random.uniform(0,1) < 0.3:
        r = random.choice(order)
    else:
        r = i-1
    q.add_edge(r, i)
    print(order.index(r))
    anal = q.depth_analysis()

    q.add_simul(r, i, order, depth)

    #for i in range(0, len(order)-1):
    #    print(-q.qvertices[order[i]].pH.pos+q.qvertices[order[i+1]].pH.pos, end=" ")

    print()

    anal_sorted = []

    for i in range(0, len(anal)):
        anal_sorted.append(anal[order[i]])

    print("cdepth\t", anal_sorted)
    print("depth\t", depth)
    

    print()
    print("order", order)


q.add_edge(0, 1)
#q.depth_analysis()
#
#q.add_simul(1, 2, order, depth)
#print("order", order)
#print("depth", depth)

q.add_edge(1, 2)
#q.depth_analysis()
#
#q.add_simul(1, 2, order, depth)
#print("order", order)
#print("depth", depth)
#
q.add_edge(0, 3)
q.depth_analysis()
#
#q.add_simul(0, 3, order, depth)
#print("order", order)
#print("depth", depth)
#
q.add_edge(0, 4)
q.depth_analysis()
#
#q.add_simul(1, 4, order, depth)
#print("order", order)
#print("depth", depth)

#q.add_edge(3, 4)
#q.depth_analysis()
#
#q.add_edge(1, 5)
#q.depth_analysis()
#
#q.add_edge(2, 6)
#q.depth_analysis()
#
#q.add_edge(2, 7)
#q.depth_analysis()
#
#q.add_edge(4, 8)
#q.depth_analysis()
#
#q.add_edge(6, 9)
#q.depth_analysis()

#q.add_edge(2, 8)
#q.depth_analysis()

#q.sink(2, q.last)
#q.depth_analysis()

q.loop.loopify()
#pcvl.pdisplay(q.loop.circuit)

'''
q.loop.calc_in_state()
q.loop.run_format()
'''
