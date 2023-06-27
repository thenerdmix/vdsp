import perceval as pcvl
import perceval.components as symb
import numpy as np
import sympy as sp

start = pcvl.Circuit(4, name="start")

start.add((0, 1), symb.BS.H())
start.add((2, 3), symb.BS.H())

fusion = pcvl.Circuit(4, name="fusion")
fusion.add((0, 1), symb.PERM([1, 0]))
fusion.add((1, 2), symb.PERM([1, 0]))
fusion.add((0, 1), symb.PERM([1, 0]))
fusion.add((0, 1), symb.BS.H())

gen = pcvl.Circuit(4, name="gen")
gen.add(0, start)
gen.add(0, fusion)

pcvl.pdisplay(fusion, recursive=True)
pcvl.pdisplay(fusion.U)