import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *

#start CNOT
cnot = pcvl.Circuit(6, name="Ralph CNOT")
#cnot.add((2, 3), symb.PERM([1, 0]))
#cnot.add((4, 5), symb.PERM([1, 0]))
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

q0 = Qbit(2, logical=False)
q1 = Qbit(4, logical=False)

p0 = Photon(type=PhotonType.SOL)
p0.set_pos(0)
p0.set_in_state(0)
p1 = Photon(type=PhotonType.SOL)
p1.set_pos(1)
p1.set_in_state(0)

photons = set([p0, p1]).union(q0.get_photons()).union(q1.get_photons())


l = Loop(photons, bsg, qbits={q0, q1})
l.calc_in_state()
print(l.in_state)


#l.fuse(q1, q2)

pcvl.pdisplay(l.circuit)

l.calc_out_states(postprocess=False)
print(l.out_states)
l.run()