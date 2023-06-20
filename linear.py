import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *

photons = 4
circ = pcvl.Circuit(photons, name='GHZ')

for i in range(photons):
    circ.add(i, symb.HWP(sp.pi / 8))

for i in range(photons-2):
    circ.add((i, i+1), symb.PBS())

#circ.add(photons-2, symb.HWP(sp.pi/8))

circ.add((photons-2, photons-1), symb.PBS())

# The Hadamard correction before measurement
for i in range(1,photons):
    circ.add(i, symb.HWP(sp.pi / 8))

pcvl.pdisplay(circ)
pcvl.pdisplay(circ.U)

l = Loop(8, circ)
l.calc_out_states()
l.run([1, 1, 1, 1])