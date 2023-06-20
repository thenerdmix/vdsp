import perceval as pcvl
import numpy as np

from Loop import *

cnot = pcvl.Circuit(4, name='Bell states')
cnot.add((0, 1), pcvl.BS.H())
cnot.add((2, 3), pcvl.BS.H())
cnot.add((0, 1), pcvl.BS.H(np.pi))
cnot.add((1, 2), pcvl.BS.H(np.pi))
cnot.add((0, 1), pcvl.BS.H(np.pi))
cnot.PERM([0,1,2,3])
pcvl.pdisplay(cnot)
pcvl.pdisplay(cnot.U)

l = Loop(4, cnot)
l.calc_out_states()
l.run([1, 1, 1, 1])