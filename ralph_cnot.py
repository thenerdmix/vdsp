import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *

def wc(n, U):
    s='aold'+str(n)+'= '
    for i in range(len(U[:,n])):
        s+=pcvl.utils.simple_float(U[i, n])[1].replace('s', 'S').replace('(','[').replace(')',']')+'*a'+str(i)
        if i < len(U[:,n])-1:
            s+= ' + '
    return(s)


#start CNOT
cnot = pcvl.Circuit(6, name="Ralph CNOT")

cnot.add((0, 1), pcvl.BS.H(2*np.pi-pcvl.BS.r_to_theta(1/3)))
cnot.add((3, 4), pcvl.BS.H())
cnot.add((2, 3), pcvl.BS.H(2*np.pi-pcvl.BS.r_to_theta(1/3)))
cnot.add((4, 5), pcvl.BS.H(pcvl.BS.r_to_theta(1/3)))

#end CNOT

cz = pcvl.Circuit(6, name='CZ')
cz.add(0, cnot, merge=True)


bsg = pcvl.Circuit(6, name='BSG')
bsg.add((1, 2), symb.BS.H())
bsg.add(0, cz, merge=True)

q0 = Qbit(1, logical=False)
q1 = Qbit(3, logical=False)

p0 = Photon(type=PhotonType.SOL)
p0.set_pos(0)
p0.set_in_state(0)
p1 = Photon(type=PhotonType.SOL)
p1.set_pos(5)
p1.set_in_state(0)

photons = set([p0, p1]).union(q0.get_photons()).union(q1.get_photons())
qbits = {q0, q1}


l = Loop(photons, bsg, qbits)
l.calc_in_state()
print(l.in_state)

print(l.out_states)

l.loopify()

pcvl.pdisplay(l.circuit, recursive=True)

l.run_format()