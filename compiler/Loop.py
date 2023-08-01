import itertools
import perceval as pcvl
import perceval.components as symb
import numpy as np

from Circuits import *

from enum import Enum

def check(photons, o, logical=True, witness=True):
    """Check if a string of 0s and 1s o corresponds to a logical string and/or the photons of type witness are witnessed correctly.

    :param photons: list of photons to check
    :type photons: list of Photon
    :param o: the string of 0s and 1s to check
    :type o: list of int
    :param logical: decide to check if the string is logical or not, defaults to True
    :type logical: bool, optional
    :param witness: decide to check if the photons of type witness must be checked or not, defaults to True
    :type witness: bool, optional
    :return: return True if the string o corresponds to the dual rail enconding of the list photons
    :rtype: bool
    """
    b = True
    for p in photons:
        if b == False:
            return b

        assert p.type != None, "Photon has no type!"
        if logical and p.type == PhotonType.COMP:
            b = (b and ((o[p.pos]==1 and o[p.other().pos]==0) or (o[p.pos]==0 and o[p.other().pos]==1)))
        elif witness and p.type == PhotonType.WITNESS:
            assert p.out_state != None, "Photon of type WITNESS has no out_state!"
            b = (b and o[p.pos]==p.out_state)
    return b

def partition(n, m):
    """Return a list of all the possible partitions of m elements in n bins.

    :param n: number of bins
    :type n: int
    :param m: number of elements to partition
    :type m: int
    :return: list of all the possible partitions
    :rtype: list of list
    """
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
    """Given a set of qubits and a state state, it returns a dictionary mapping every qubit to the corresponding logical state.

    :param qbits: list of qubits
    :type qbits: list of Qubit
    :param state: a Fock state
    :type state: list of int
    :return: a dictionary mapping every qubit to False or True
    :rtype: dict
    """
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
    """Given a list of qubits, return the list of corresponding photons.

    :param qbits: list of qubits
    :type qbits: list of Qubit
    :return: list of photons
    :rtype: list of Photon
    """
    photons = []
    for q in qbits:
        photons += q.get_photons()
    return photons

def photon_from_position(photons, pos):
    """Return the photon with position pos in a list of photons.

    :param photons: list of photons
    :type photons: list of Photon
    :param pos: position of the photon in the photonic circuit
    :type pos: int
    :return: photon in position pos
    :rtype: Photon
    """
    for p in photons:
        if p.pos == pos:
            return p

class PhotonType(Enum):
    """There are three possible types of photons. 1) Photons that belong to a qubit (COMPutational photons), 2) Photons that will be witnessed (WITNESS), 3) Everything else.
    Photons of type COMP will always have a corresponding Qubit object and a corresponding polariation Horizontal or Vertical.
    Photon of type WITNESS will always have a out_state.
    """
    COMP = "COMP"
    WITNESS = "WITNESS"
    NONE = "99"

    def __str__(self):
        return self.name


class PhotonPolarization(Enum):
    """Photons of type COMP in the dual rail enconding can either correspond to the Horizontal or Vertical polarization in the polarization enconding.
    """
    H = "H"
    V = "V"
    NONE = "99"


class Qbit(object):
    newid = itertools.count()

    def __init__(self, pos, logical=False):
        self.pH = Photon(type=PhotonType.COMP)
        self.pH.pos = pos

        self.pV = Photon(type=PhotonType.COMP)
        self.pV.pos = pos+1

        if not logical:
            self.pH.in_state = 1
            self.pV.in_state = 0
        else:
            self.pH.in_state = 0
            self.pV.in_state = 1

        self.pH.polarization = PhotonPolarization.H
        self.pV.polarization = PhotonPolarization.V

        self.pH.qubit = self
        self.pV.qubit = self

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

        self.qubit = None
        self.polarization = None

    def set_in_state(self, in_state):
        self.in_state = in_state

    def set_pos(self, pos):
        self.pos = pos

    def set_witness(self, out_state):
        self.type = PhotonType.WITNESS
        self.out_state =  out_state
        self.qubit = None

    def other(self):
        assert self.type == PhotonType.COMP, "Trying to get the other photon of a non COMP photon"
        if self.polarization==PhotonPolarization.H:
            return self.qubit.pV
        elif self.polarization==PhotonPolarization.V:
            return self.qubit.pH
        else:
            assert True, "Polarization not set properly!"

class Loop(object):

    def __init__(self, photons=[], qbits=[], circuit=None):
        self.in_state = None
        self.out_states = []

        self.circuit = circuit

        self.photons = photons
        self.qbits = qbits

        self.nph = 0

        self.unitaries = []

    def swap_photons(self, pos1, pos2):
        assert pos2-pos1==1, "The two swap positions are not near!!!"
        p1 = photon_from_position(self.photons, pos1)
        p2 = photon_from_position(self.photons, pos2)

        self.circuit.add((p1.pos, p2.pos), symb.BS.H(np.pi), merge=True)

        p1.type, p2.type = p2.type, p1.type
        p1.out_state, p2.out_state = p2.out_state, p1.out_state

        if p1.qubit != None:
            if p1.polarization == PhotonPolarization.H:
                p1.qubit.pH = p2
            elif p1.polarization == PhotonPolarization.V:
                p1.qubit.pV = p2
            else:
                assert True, "The photon is associated to a qubit but doesn't have a polarization!"

        if p2.qubit != None:
            if p2.polarization == PhotonPolarization.H:
                p2.qubit.pH = p1
            elif p2.polarization == PhotonPolarization.V:
                p2.qubit.pV = p1
            else:
                assert True, "The photon is associated to a qubit but doesn't have a polarization!"

        p1.qubit, p2.qubit = p2.qubit, p1.qubit
        p1.polarization, p2.polarization = p2.polarization, p1.polarization


    def sink(self, q1:Qbit, q2:Qbit):
        start = q1.pH.pos
        end = q2.pV.pos
        for i in range(start, end):
            self.swap_photons(i, i+1)

        for i in range(start, end):
            self.swap_photons(i, i+1)


    def add_bs(self, name="bsg", q0_id = None, q1_id = None):
        if self.circuit != None:
            temp = self.circuit
            self.circuit = pcvl.Circuit(len(self.photons)+4)
            self.circuit.add(0, temp, merge=True)
            self.circuit.add(len(self.photons), bp_circuit(name), merge=False)
        else:
            self.circuit = bp_circuit(name)

        q0 = Qbit(len(self.photons), logical=False)
        q1 = Qbit(len(self.photons)+2, logical=False)

        q0.id = q0_id
        q1.id = q1_id

        self.photons+=[*q0.get_photons(), *q1.get_photons()]
        self.qbits+=[q0, q1]

        return q0, q1

    def calc_in_state(self):
        in_state = [None]*len(self.photons)
        for p in self.photons:
                assert p.in_state != None, "Photon was not initialized correctly"
                in_state[p.pos] = p.in_state
                self.nph += p.in_state
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

        self.circuit.add((q1.pH.pos, q1.pV.pos), symb.BS.H())

        q1.pH.set_witness(out_state=1)
        q1.pV.set_witness(out_state=0)

        #q1 is no longer a qbit
        self.qbits.remove(q1)

    def fuse2(self, q1:Qbit, q2:Qbit):
        if q1.pH.pos > q2.pH.pos:
            pos1 = q2.pH.pos
            pos2 = q1.pH.pos
        else:
            pos1 = q1.pH.pos
            pos2 = q2.pH.pos

        self.circuit.add((pos1, pos1+1), symb.BS.H())
        self.circuit.add((pos2, pos2+1), symb.BS.H())

        for i in range(pos2-pos1):
            self.circuit.add((pos1+i, pos1+i+1), symb.BS.H(np.pi))

        for i in range(pos2-pos1-1):
            self.circuit.add((pos2-i-2, pos2-i-1), symb.BS.H(np.pi))

        self.circuit.add((pos1, pos1+1), symb.BS.H())
        self.circuit.add((pos2, pos2+1), symb.BS.H())

        q1.pH.set_witness(out_state=1)
        q1.pV.set_witness(out_state=0)
        
        q2.pH.set_witness(out_state=1)
        q2.pV.set_witness(out_state=0)

        self.qbits.remove(q1)
        self.qbits.remove(q2)

        
    def calc_out_states(self, logical, witness):
        if logical or witness:
            for l in partition(self.nph, len(self.photons)):
                if check(self.photons, l, logical=logical, witness=witness):
                    self.out_states.append(l)
        else:
            for l in partition(self.nph, len(self.photons)):
                self.out_states.append(l)


    def run(self, logical=True, witness=True):
        self.calc_out_states(logical, witness)
        for o in self.out_states:
            p = self.ampli(self.in_state, o)
            if(abs(p) > 10e-10):
                print(o)
                print(p)

    def run_format(self):
        assert self.in_state != None, print("The input state is NONE!")
        product_space = [[True, False]]*len(self.qbits)
        for element in itertools.product(*product_space):
            o = [None]*len(self.photons)
            for p in self.photons:
                if p.type == PhotonType.WITNESS:
                    o[p.pos] = p.out_state
                elif p.type == PhotonType.COMP:
                    index = self.qbits.index(p.qubit)
                    if element[index] == True:
                        if p.polarization == PhotonPolarization.H:
                            o[p.pos] = 0
                        elif p.polarization == PhotonPolarization.V:
                            o[p.pos] = 1
                    elif element[index] == False:
                        if p.polarization == PhotonPolarization.H:
                            o[p.pos] = 1
                        elif p.polarization == PhotonPolarization.V:
                            o[p.pos] = 0
                else:
                    assert False, print("Some photon is still of NONE type...")

            p = self.ampli(self.in_state, o)
            if(abs(p) > 10e-10):
                dic = format_logical(self.qbits, o)

                for key in sorted(dic):
                    print(key, dic[key], end=" ")
                print()
                print(p)


    def ampli(self, in_state = [], out_state = [], backend="Naive"):
        backend = pcvl.BackendFactory.get_backend(backend)
        sim = backend(self.circuit)
        return(sim.probampli_be(input_state=pcvl.BasicState(in_state), output_state = pcvl.BasicState(out_state)))

    def loopify(self, display = True):
        last = [None]*len(self.photons)
        loop = {}
        for u in self.circuit._components:
            if (last[u[0][0]] == None) and (last[u[0][1]] == None):
                loop[u] = 0
            elif last[u[0][0]] == last[u[0][1]]:
                loop[u] = loop[last[u[0][0]]]
            else:
                l1 = 0
                l2 = 0
                if last[u[0][0]] != None:
                    l1 = loop[last[u[0][0]]]
                if last[u[0][1]] != None:
                    l2 = loop[last[u[0][1]]]
            
                l = max(l1, l2+1)
            
                loop[u] = l

            last[u[0][0]] = last[u[0][1]] = u

        sorted_loop = dict(sorted(loop.items(), key=lambda x: x[1]))

        self.circuit = pcvl.Circuit(len(self.photons))

        current_loop = 0
        for s in sorted_loop:
            if(current_loop != sorted_loop[s]):
                if display:
                    self.circuit.add(0, symb.PERM(list(range(len(self.photons)))))
                current_loop = sorted_loop[s]

            self.circuit.add(s[0], s[1]) 

        depth = [0]*len(self.photons)
        for p in self.photons:
            if last[p.pos] != None:
                depth[p.pos] = loop[last[p.pos]]
            else:
                depth[p.pos] = 0

        return depth, last

