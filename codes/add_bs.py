import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

from Loop import *

l = Loop()
temp, temp, q0, q1= l.add_bs()
temp, temp, q2, q3 = l.add_bs()

l.fuse(q1, q2)
l.fuse(q2, q3)

pcvl.pdisplay(l.circuit, recursive=True)

l.calc_in_state()

l.run(witness=True, logical=False)
#l.run_format()