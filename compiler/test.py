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


'''
N = 40
for i in range(1, N):
    if random.uniform(0,1) < 0.999:
        r = random.choice(order)
    else:
        r = i-1

    q.add_edge(r, i)
    q.add_simul(r, i, order, depth)

    print()
'''

q.add_overall(0, 1, order, depth)
q.add_overall(1, 2, order, depth)
q.add_overall(2, 3, order, depth)
q.add_overall(2, 4, order, depth)
q.add_overall(1, 5, order, depth)
q.add_overall(5, 6, order, depth)
q.add_overall(5, 7, order, depth)
q.add_overall(0, 8, order, depth)
q.add_overall(8, 9, order, depth)
q.add_overall(9, 10, order, depth)
q.add_overall(10, 11, order, depth)


q.loop.loopify()
pcvl.pdisplay(q.loop.circuit)

'''
q.loop.calc_in_state()
q.loop.run_format()
'''
