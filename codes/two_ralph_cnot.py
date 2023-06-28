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

p0 = Photon(type=PhotonType.SOL)
p0.set_pos(0)
p0.set_in_state(0)
p1 = Photon(type=PhotonType.SOL)
p1.set_pos(1)
p1.set_in_state(0)
q0 = Qbit(2, logical=False)
q1 = Qbit(4, logical=False)

p2 = Photon(type=PhotonType.SOL)
p2.set_pos(6)
p2.set_in_state(0)
p3 = Photon(type=PhotonType.SOL)
p3.set_pos(7)
p3.set_in_state(0)
q2 = Qbit(8, logical=False)
q3 = Qbit(10, logical=False)

fuse = pcvl.Circuit(12, name="fuse")
fuse.add(0, bsg)
fuse.add(6, bsg)


photons = {p0, p1, p2, p3, q0.pH, q0.pV, q1.pH, q1.pV, q2.pH, q2.pV, q3.pH, q3.pV}
qbits = {q0, q1, q2, q3}

l = Loop(photons, fuse, qbits)

l.calc_in_state()
print(l.in_state)

l.fuse(q1, q2)
l.fuse(q0, q3)
pcvl.pdisplay(l.circuit, recursive=True)

l.calc_out_states()

l.run_format()