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


photons = 12

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


fusion = pcvl.Circuit(12, name="FUSION")
fusion.add(0, bsg)
fusion.add(6, bsg)

pcvl.pdisplay(fusion, recursive=True)
pcvl.pdisplay(fusion.U)
print(wc(2, fusion.U))
print(wc(4, fusion.U))

l = Loop(photons, bsg)
l.calc_out_states(mode=2)
l.run_ampli(pcvl.BasicState([0, 0, 1, 0, 1, 0]))