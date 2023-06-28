import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

def build_cnot():
    bsg = pcvl.Circuit(6, name="RalphBSG")
    
    bsg.add((1,2), pcvl.BS.H())
    bsg.add((0, 1), pcvl.BS.H(2*np.pi-pcvl.BS.r_to_theta(1/3)))
    bsg.add((3, 4), pcvl.BS.H())
    bsg.add((2, 3), pcvl.BS.H(2*np.pi-pcvl.BS.r_to_theta(1/3)))
    bsg.add((4, 5), pcvl.BS.H(pcvl.BS.r_to_theta(1/3)))

    return bsg