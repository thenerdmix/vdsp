import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *
from Ralph import *

n = 3
photons = n*6

circ = pcvl.Circuit(photons)
qbits = []
photons = []

for i in range(n):
    add = [Photon(type=PhotonType.SOL), Photon(type=PhotonType.SOL)]
    add[0].set_in_state(0)
    add[0].set_pos(6*i)
    add[1].set_in_state(0)
    add[1].set_pos(6*(i+1)-1)
    photons += add
    qbits += [Qbit(6*i+1, logical=False), Qbit(6*i+3, logical=False)]
    circ.add(i*6, build_cnot(), merge=True)

#!!! I must copy the list because the fuse method actually deletes some qbits
l = Loop(circuit=circ, photons=photons+photons_from_qubit(qbits), qbits=qbits.copy())

l.calc_in_state()
print(l.in_state)

print(len(qbits))
l.fuse(qbits[0], qbits[2])
l.fuse(qbits[2], qbits[4])

pcvl.pdisplay(l.circuit, recursive = True)

l.run(logical=False, witness=True)