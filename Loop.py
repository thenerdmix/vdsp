import itertools
import perceval as pcvl
import perceval.components as symb
import numpy as np

from Ralph import build_cnot

from enum import Enum

def check(photons, o, logical=True, witness=True):
    b = True
    for p in photons:
        assert p.type != None, "Photon has no type!"
        if logical and p.type == PhotonType.COMP:
            b = b and ((o[p.pos]==1 and o[p.other.pos]==0) or (o[p.pos]==0 and o[p.other.pos]==1))
        elif witness and p.type == PhotonType.WITNESS:
            assert p.out_state != None, "Photon of type WITNESS has no out_state!"
            b = b and o[p.pos]==p.out_state
    return b

def partition(n, m):
    result = []

    def backtrack(curr_list, remaining_sum, remaining_length):
        if remaining_length == 0:
            if remaining_sum == 0:
                result.append(curr_list)
            return

        for i in range(remaining_sum + 1):
            if i <= remaining_sum:
                backtrack(curr_list + [i], remaining_sum - i, remaining_length - 1)

    backtrack([], n, m)
    return result

def format_logical(qbits, state):
    res = {}
    for q in qbits:
        if(state[q.pH.pos]==1 and state[q.pV.pos]==0):
            res[q.id] = False
        elif(state[q.pH.pos]==0 and state[q.pV.pos]==1):
            res[q.id] = True
        else:
            res[q.id] = None
            print("There is a non logical code!")
    return res

def photons_from_qubit(qbits):
    photons = []
    for q in qbits:
        photons += q.get_photons()
    return photons

class PhotonType(Enum):
    COMP = "COMP"
    WITNESS = "WITNESS"
    SOL = "SOL"
    NONE = "99"

    def __str__(self):
        return self.name

class Qbit(object):
    newid = itertools.count()

    def __init__(self, pos, logical=False):
        self.id = next(Qbit.newid)

        self.pH = Photon(type=PhotonType.COMP)
        self.pH.pos = pos

        self.pV = Photon(type=PhotonType.COMP)
        self.pV.pos = pos+1

        self.pH.other = self.pV
        self.pV.other = self.pH

        if not logical:
            self.pH.in_state = 1
            self.pV.in_state = 0
        else:
            self.pH.in_state = 0
            self.pV.in_state = 1

    def get_photons(self):
        return [self.pH, self.pV]

class Photon(object):
    newid = itertools.count()

    def __init__(self, type:PhotonType):
        self.id = next(Photon.newid)
        self.pos = self.id
        self.type = type
        self.in_state = None
        self.out_state = None
        self.other = None

    def set_in_state(self, in_state):
        self.in_state = in_state

    def set_pos(self, pos):
        self.pos = pos

    def set_witness(self, out_state):
        self.out_state =  out_state

class Loop(object):

    def __init__(self, photons=[], circuit=None, qbits=[]):
        self.in_state = None
        self.out_states = []

        self.circuit = circuit

        self.photons = photons
        self.qbits = qbits

        self.n_out = 0

    def add_bs(self):
        if self.circuit != None:
            temp = self.circuit
            self.circuit = pcvl.Circuit(len(self.photons)+6)
            self.circuit.add(0, temp)
            self.circuit.add(len(self.photons), build_cnot())


        else:
            self.circuit = build_cnot()

        p0 = Photon(type=PhotonType.SOL)
        p0.set_pos(len(self.photons))
        p0.set_in_state(0)
        p1 = Photon(type=PhotonType.SOL)
        p1.set_pos(len(self.photons)+1)
        p1.set_in_state(0)

        q0 = Qbit(len(self.photons)+2, logical=False)
        q1 = Qbit(len(self.photons)+4, logical=False)

        self.photons+=[p0, p1, *q0.get_photons(), *q1.get_photons()]
        self.qbits+=[q0, q1]

        return p0, p1, q0, q1

    def calc_in_state(self):
        in_state = [None]*len(self.photons)
        for p in self.photons:
                assert p.in_state != None, "Photon was not initialized correctly"
                in_state[p.pos] = p.in_state
                self.n_out += p.in_state
        self.in_state = in_state

    def fuse(self, q1:Qbit, q2:Qbit):
        #The first qbit will be witnessed!
        if q1.pH.pos > q2.pH.pos:
            pos1 = q2.pH.pos
            pos2 = q1.pH.pos
        else:
            pos1 = q1.pH.pos
            pos2 = q2.pH.pos

        for i in range(pos2-pos1):
            self.circuit.add((pos1+i, pos1+i+1), symb.BS.H(np.pi))

        for i in range(pos2-pos1-1):
            self.circuit.add((pos2-i-2, pos2-i-1), symb.BS.H(np.pi))

        self.circuit.add((pos1, pos1+1), symb.BS.H())

        q1.pH.type = PhotonType.WITNESS
        q1.pH.set_witness(out_state=1)
        q1.pV.type = PhotonType.WITNESS
        q1.pV.set_witness(out_state=0)

        #q1 is no longer a qbit
        self.qbits.remove(q1)


        
    def calc_out_states(self, logical, witness):
        if logical or witness:
            for l in partition(self.n_out, len(self.photons)):
                if check(self.photons, l, logical=logical, witness=witness):
                    self.out_states.append(l)
        else:
            for l in partition(self.n_out, len(self.photons)):
                self.out_states.append(l)


    def run(self, logical=True, witness=True):
        self.calc_out_states(logical, witness)
        for o in self.out_states:
            p = self.ampli(self.in_state, o)
            if(abs(p) > 10e-3):
                print(o)
                print(p)

    def run_format(self):
        self.calc_out_states(True, True)
        for o in self.out_states:
            p = self.ampli(self.in_state, o)
            if(abs(p) > 10e-3):
                dic = format_logical(self.qbits, o)

                for key in sorted(dic):
                    print(key, dic[key], end=" ")
                print()
                print(p)

    def ampli(self, in_state = [], out_state = [], backend="Naive"):
        backend = pcvl.BackendFactory.get_backend(backend)
        sim = backend(self.circuit)
        return(sim.probampli_be(input_state=pcvl.BasicState(in_state), output_state = pcvl.BasicState(out_state)))