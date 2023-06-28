import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *

circ = pcvl.Circuit(8, "fusion")
q1 = Qbit(0, logical=False)
q2 = Qbit(2, logical=False)
q3 = Qbit(4, logical=False)
q4 = Qbit(6, logical=False)

photons = q1.get_photons().union(q2.get_photons()).union(q3.get_photons()).union(q4.get_photons())

l = Loop(photons, circ)
l.fuse(q1, q4)
pcvl.pdisplay(l.circuit, recursive=True)
l.calc_in_state()
print(l.in_state)
l.calc_out_states()
print(l.out_states)

l.run()
