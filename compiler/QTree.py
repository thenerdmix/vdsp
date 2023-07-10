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
            anal = [None]*len(self.qvertices)
            for v in self.qvertices:
                ph = self.loop.loopify(display=False)[self.qvertices[v].pH.pos]
                pv = self.loop.loopify(display=False)[self.qvertices[v].pH.pos]
                if(ph==pv):
                    d = ph
                else:
                    d = max(ph, pv+1)

                if d==0:
                    d+=1

                #print("vertex:", v, "depth:", d)
                #print()

                anal[v] = d
                
            return anal

        def add_simul(self, parent, leaf, order, depth):
            if order.index(parent) < len(order)-1:
                m = depth[order.index(parent)]-1
                for i in range(order.index(parent)+1, len(order)):
                    m = max(m, depth[i])
                    depth[i-1] = m+2
                    order[i-1] = order[i]
                order[len(order)-1] = parent
                depth[len(order)-1] = m+2
                
            depth[len(order)-1] += 1

            order.append(leaf)
            depth.append(1)
