import perceval as pcvl
import perceval.components as symb
import numpy as np

def bp_circuit(name=None):
    bp = pcvl.Circuit(4, name=name)
    
    bp.add((0,1), pcvl.BS.H())
    bp.add((2,3), pcvl.BS.H())

    bp.add((0, 1), symb.BS.H(np.pi))
    bp.add((1, 2), symb.BS.H(np.pi))
    bp.add((2, 3), symb.BS.H())

    bp.add((0, 1), symb.BS.H(np.pi))

    return bp

#pcvl.pdisplay(bp_circuit())