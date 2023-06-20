import itertools
import perceval as pcvl

from enum import Enum

'''
def is_logical(state):
    for i in state:
        if not (i==0 or i==1):
            print('Invalid logical state')
            return False
    return True

def is_photon(state):
    if len(state)%2 != 0:
        return False

def logical_photon(state):
    output = []
    for i in state:
        if i==0:
            print('ok')
            output+=[0, 1]
        elif i==1:
            output+=[1, 0]
        else:
            print('Invalid logical state')
            return None
    return output

def photon_logical(state):
    output = []
    if len(state)%2 != 0:
            print('Invalid photon state')
            return None

    for i in range(0, len(state), 2):
        if state[i]==0 and state[i+1]==1:
            output+=[0]
        elif state[i]==1 and state[i+1]==0:
            output+=[1]
        else:
            print('Invalid photon state')
            return None
    return output
'''
def check(photons, o):
    b = True
    for p in photons:
        assert p.type != None, "Photon has no type!"
        if p.type == PhotonType.COMP:
            b = b and ((o[p.pos]==1 and o[p.other.pos]==0) or (o[p.pos]==0 and o[p.other.pos]==1))
        elif p.type == PhotonType.WITNESS:
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
        return {self.pH, self.pV}

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

    def __init__(self, photons, circuit):
        self.in_state = None
        self.out_states = []
        self.circuit = circuit
        self.photons = photons
        self.n_out = 0

    def calc_in_state(self):
        in_state = [None]*len(self.photons)
        for p in self.photons:
                assert p.in_state != None, "Photon was not initialized correctly"
                in_state[p.pos] = p.in_state
                self.n_out += p.in_state
        self.in_state = in_state

         
        
    def calc_out_states(self):
        for l in partition(self.n_out, len(self.photons)):
            if check(self.photons, l):
                self.out_states.append(l)

    def run(self):
        for o in self.out_states:
            p = self.ampli(self.in_state, o)
            print(o)
            print(p)

    def ampli(self, in_state = [], out_state = [], backend="Naive"):
        backend = pcvl.BackendFactory.get_backend(backend)
        sim = backend(self.circuit)
        return(sim.probampli_be(input_state=pcvl.BasicState(in_state), output_state = pcvl.BasicState(out_state)))