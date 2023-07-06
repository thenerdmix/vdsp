from Loop import *
from Graph import *

import perceval as pcvl
import perceval.components as symb

class QTree:
        def __init__(self, head_id):
            self.loop = None

            self.qvertices = {}
            
            circuit = pcvl.Circuit(2)
            circuit.add((0, 1), symb.BS.H())

            head_qubit = Qbit(pos=0, logical=False)

            self.qvertices[head_id] = head_qubit
            head_qubit.id = head_id
        
            self.loop = Loop(photons=photons_from_qubit([head_qubit]), qbits=[head_qubit], circuit=circuit)

            #keep in mind the last vertex that was added to the tree
            self.last = head_id
        

        def sink(self, up, down):
            q_up = self.qvertices[up]
            q_down = self.qvertices[down]

            self.loop.sink(q_up, q_down) 

        def add_edge(self, parent, leaf, sink=True):
            print("ADDING EDGE", parent, leaf)
            #the qbit parent must be already present in the tree
            #sink the parent vertex to the bottom (the last position), if they are different
            if(sink and (self.last != parent)):
                self.sink(parent, self.last)

            qlost, qleaf = self.loop.add_bs(q0_id = None, q1_id = leaf)

            #the newly created qbit leaf is added to the tree
            self.qvertices[leaf] = qleaf
            self.last = leaf

            self.loop.fuse(qlost, self.qvertices[parent])

            #put the parent at the end of the circuit
            #self.sink(parent, leaf)
            #self.last = parent

        def depth_analysis(self):
            for v in self.qvertices:
                print("vertex:", v, "depth:", self.loop.loopify(display=False)[self.qvertices[v].pH.pos])
                print()