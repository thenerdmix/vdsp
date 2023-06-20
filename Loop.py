import itertools

import perceval as pcvl

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

'''
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

class Loop(object):

    def __init__(self, width, circuit):
        self.width=width
        self.in_state = None
        self.out_states = []
        self.circuit = circuit
        
    def calc_out_states(self, mode=2):
        base = range(mode)
        a = itertools.product(base, repeat=self.width)
        for i in a:
            self.out_states.append(list(i))

    def run_prob(self, in_state = [], backend='Naive'):
        backend = pcvl.BackendFactory.get_backend(backend)
        sim = backend(self.circuit)
        for o in self.out_states:
            p = sim.prob(input_state=in_state, output_state = pcvl.BasicState(o))
            if(p != 0.0):
                print(o)
                print(p)
                print()

    def run_ampli(self, in_state = [], backend="Naive"):
        backend = pcvl.BackendFactory.get_backend(backend)
        sim = backend(self.circuit)
        for o in self.out_states:
            p = sim.probampli_be(input_state=in_state, output_state = pcvl.BasicState(o))
            if(p != 0.0):
                print(o)
                print(p)
                print()
