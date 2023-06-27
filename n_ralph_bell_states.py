import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *
from Ralph import *

n = 4
photons = n*6

circ = pcvl.Circuit(photons)
qbits = []
photons = []

for i in range(n):
    add = [Photon(type=PhotonType.SOL), Photon(type=PhotonType.SOL)]
    add[0].set_in_state(0)
    add[0].set_pos(6*i)
    add[1].set_in_state(0)
    add[1].set_pos(6*i+1)
    photons += add
    qbits += [Qbit(6*i+2, logical=False), Qbit(6*i+4, logical=False)]
    circ.add(i*6, build_cnot())

l = Loop(circuit=circ, photons=photons+photons_from_qubit(qbits), qbits=qbits)

l.calc_in_state()
print(l.in_state)

pcvl.pdisplay(l.circuit, recursive = True)