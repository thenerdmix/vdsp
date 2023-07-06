from Graph import *
from Loop import *
from QTree import *

from qiskit import transpile, QuantumCircuit
import perceval as pcvl

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

q.add_edge(0, 1)
q.depth_analysis()

q.add_edge(1, 2)
q.depth_analysis()

q.add_edge(2, 3)
q.depth_analysis()

q.add_edge(3, 4)
q.depth_analysis()

q.add_edge(4, 5)
q.depth_analysis()


#q.add_edge(2, 8)
#q.depth_analysis()

#q.sink(2, q.last)
#q.depth_analysis()

pcvl.pdisplay(q.loop.circuit)

'''
q.loop.calc_in_state()
q.loop.run_format()
'''
