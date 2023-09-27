from Loop import *
from Graph import *

import perceval as pcvl
import perceval.components as symb


def build_optimal(node, qtree):
    """Build the optimal DFS-ordered circuit on the object qtree. The idea is to order each vertex's children, recursively computing the weight of the subtrees. To compute the weight of the subtree we lunch the function on a newly created QTree object.

    :param node: the head of the subtree we are building
    :type node: TreeNode
    :param qtree: the QTree object in which we are building the circuit
    :type qtree: QTree
    :return: the number of outer loops needed to build the subtree with head the TreeNode head. We compute it 
    :rtype: int
    """
    node.children.sort(key=lambda x: build_optimal(x, QTree(head_id = x.value)), reverse=False)
    for c in node.children:
        qtree.add_edge(node.value, c.value)
        build_optimal(c, qtree)
    return max(qtree.depth().values())

class QTree:
    """A QTree (=Quantum Tree) is made of a normal tree, a Loop object containing the Qubit objects and the circuit of the problem and a map qvertices that map the vertices id to the corresponding Loop.Qbbit object.

    :param loop: the Loop object associated to the Quantum Tree
    :type loop: Loop
    :param qvertices: a dictionary that maps the vertices id to the corresponding Qubit objects
    :type qvertices: a dictionary where keys are int and values are Loop.Qbit object
    :param last: the id of the last vertex in the photonic circuit
    :type last: int
    """ 
    def __init__(self, head_id):
        """Constructor method. When initializing a Quantum Tree we start with a qubit initialized in the state + (hence the Hadamard gate) and we label with this qubit with the integer index head_id"""
        self.loop = None
        self.qvertices = {}
        
        circuit = pcvl.Circuit(2)
        circuit.add((0, 1), symb.BS.H())

        head_qubit = Qbit(pos=0, logical=False)

        self.qvertices[head_id] = head_qubit
        head_qubit.id = head_id
    
        self.loop = Loop(photons=photons_from_qubit([head_qubit]), qbits=[head_qubit], circuit=circuit)

        #keep in mind the last vertex that was added to the tree. We will need this to sink qubits at the end of the circuit.
        self.last = head_id
    

    def sink(self, up, down):
        """Sink the qubit with integer index up to the position of the qubit with integer position down.

        :param up: position of the upper qubit
        :type up: int
        :param down: position of the lower qubit
        :type down: int
        """
        q_up = self.qvertices[up]
        q_down = self.qvertices[down]

        self.loop.sink(q_up, q_down) 

    def add_edge(self, parent, leaf, sink=True):
        """Add an edge between the qubits with index parent and leaf. The qubit with index leaf will be newly created. The qbit parent must be already present in the tree.

        :param parent: index of the parent qubit
        :type parent: int
        :param leaf: index of the leaf qubit
        :type leaf: int
        :param sink: you can decide to perform the fusion with or without sinking the parent qubit to the bottom of the circuit, defaults to True
        :type sink: bool, optional
        """

        #sink the parent vertex to the bottom (the last position), if they are different
        if(sink and (self.last != parent)):
            self.sink(parent, self.last)

        qlost, qleaf = self.loop.add_bs(q0_id = None, q1_id = leaf)

        #the newly created qbit leaf is added to the tree
        self.qvertices[leaf] = qleaf
        self.last = leaf

        self.loop.fuse(qlost, self.qvertices[parent])

    def cdepth(self):
        """Given two photonic lines representing a qubit, we can calculate in which outer loop the last optical element on this two lines is positioned (cdepth = calculated depth).

        :return: it returns a list mapping every qubit index to the corresponding outer loop number defined above.
        :rtype: int
        """
        cdepth = {}
        for v in self.qvertices:
            depth, last = self.loop.loopify(display=False)
            ph = depth[self.qvertices[v].pH.pos]
            pv = depth[self.qvertices[v].pV.pos]

            assert(ph == pv)

            d = ph

            if d==0:
                d+=1

            cdepth[v] = d

        return cdepth
           

### this last two functions are not really useful. I used them to prove the correctness of the algorithm describing how the number of loops grows.
    def add_simul(self, parent, leaf, order, depth):
        text_file = open("./compiler/output.txt", "a")
        """This function simulates algorithmically the growth of the circuit when adding an edge.

        :param parent: id of the parent qubit
        :type parent: int
        :param leaf: id of the leaf qubit
        :type leaf: int
        :param order: a list that keeps the order of the qubit in the photonic circuit (starting from above)
        :type order: list of int
        :param depth: a list recording the depth of every qubit's lines (as defined above)
        :type depth: list of int
        """
        if order.index(parent) < len(order)-1:
            m = depth[order.index(parent)]
            for i in range(order.index(parent)+1, len(order)):
                m = max(m, depth[i]+1)
                depth[i-1] = m+1
                order[i-1] = order[i]
            order[len(order)-1] = parent
            depth[len(order)-1] = m+1

        depth[len(order)-1] += 1

        order.append(leaf)
        depth.append(1)

        cdepth = self.cdepth()
        cdepth_sorted = []

        for i in range(0, len(depth)):
            cdepth_sorted.append(cdepth[order[i]])
        print(parent, "→",leaf, file=text_file)
        print(*order, sep="\t", file=text_file)
        print(*depth, sep="\t", file=text_file)
        text_file.close()

    def add_overall(self, parent, leaf, order, depth):
        self.add_edge(parent, leaf)
        self.add_simul(parent, leaf, order, depth)