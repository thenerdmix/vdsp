import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *

n = 3
photons = n*2
circ = pcvl.Circuit(photons, name='GHZ')
for i in range(n):
    circ.add((2*i, 2*i+1), symb.BS.H())

for i in range(n-1):
    circ.add((2*i, 2*i+1), symb.BS.H(np.pi))
    circ.add((2*i+1, 2*i+2), symb.BS.H(np.pi))
    circ.add((2*i, 2*i+1), symb.BS.H(np.pi))

pcvl.pdisplay(circ)

qbits = [Qbit(2*i, logical=False) for i in range(n)]

l = Loop(circuit=circ, photons=photons_from_qubit(qbits), qbits=qbits)

l.calc_in_state()

#l.run_format()
l.run(logical=False)