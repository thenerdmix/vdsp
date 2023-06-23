import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

def build_cnot():
    cnot = pcvl.Circuit(6, name="Ralph CNOT")
    cnot.add(0, symb.PERM([0, 5, 1, 2, 3, 4]))

    cnot.add((0, 1), pcvl.BS.H(2*np.pi-pcvl.BS.r_to_theta(1/3)))
    cnot.add((3, 4), pcvl.BS.H())
    cnot.add((2, 3), pcvl.BS.H(2*np.pi-pcvl.BS.r_to_theta(1/3)))
    cnot.add((4, 5), pcvl.BS.H(pcvl.BS.r_to_theta(1/3)))
    cnot.add((3, 4), pcvl.BS.H())

    cnot.add(0, symb.PERM([0, 2, 3, 4, 5, 1]))
    cnot.add((2, 3), symb.PERM([1, 0]))
    cnot.add((4, 5), symb.PERM([1, 0]))
    #end CNOT

    cz = pcvl.Circuit(6, name='CZ')
    cz.add((4, 5), symb.BS.H())
    cz.add(0, cnot, merge=False)
    cz.add((4, 5), symb.BS.H())


    bsg = pcvl.Circuit(6, name='BSG')
    bsg.add((2, 3), symb.BS.H())
    bsg.add((4, 5), symb.BS.H())
    bsg.add(0, cz)

    return bsg