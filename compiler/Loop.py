import itertools
import perceval as pcvl
import perceval.components as symb
import numpy as np
import networkx as nx

from compiler.PhotonicQubit import photon_from_position, PhotonPolarization, PhotonType, Qbit, check, format_logical
from compiler.Circuits import *
from perceval.utils import StateGenerator, Encoding

from pprint import pprint


class Loop(object):
    """An object that manages a physical photonic circuit.
    
    :param in_state: the input Fock state
    :type in_state: list of int
    :param out_state: a list of Fock states to be tested as outputs
    :type out_state: list of Fock states
    :param circuit: the Perceval circuit
    :type circuit: Perceval.Circuit
    :param photons: a set of photonic lines
    :type photons: a list of Photon objects
    :param qbits: a set of logical qbits
    :type qbits: a list of Qbit objects
    :param nph: number of input photons
    :type nph: int

    """
    def __init__(self, photons=[], qbits=[], circuit=None):
        self.in_state = None
        self.out_states = []
        self.circuit = circuit
        self.photons = photons
        self.qbits = qbits
        self.nph = 0

    def swap_photons(self, pos1, pos2):
        """A function to swap thow phonic lines positioned at pos1 and pos2. The must be next to each other.

        :param pos1: position of the first photonic line
        :type pos1: int
        :param pos2: position of the second photonic line to swap with the first one
        :type pos2: int
        """
        assert pos2-pos1==1, "The two swap positions are not near!!!"
        p1 = photon_from_position(self.photons, pos1)
        p2 = photon_from_position(self.photons, pos2)

        #add the swap in the circuit
        self.circuit.add((p1.pos, p2.pos), symb.BS.H(np.pi), merge=True)

        #the two lines must swap type
        p1.type, p2.type = p2.type, p1.type
        #and out_state if they are of WITNESS type
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
        """Sink the qubit q1 to the position of qubit q2

        :param q1:
        :type q1: Qbit
        :param q2:
        :type q2: Qbit
        """
        start = q1.pH.pos
        end = q2.pV.pos
        for i in range(start, end):
            self.swap_photons(i, i+1)

        for i in range(start, end):
            self.swap_photons(i, i+1)


    def add_bs(self, name="bsg", q0_id = None, q1_id = None):
        """Add a two vertices graph state, creating two qubits q1 and q2 and labelling the two vertices with ids q0_id and q1_id
        """
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
    
    def add_ghz_cluster(self, name="ghzs", q0_id = None, q1_id=None, q2_id = None):
        """adds space for a ghz cluster (we do not generate the cluster itself instead we assume it as the given input)"""
        if self.circuit != None:
            temp = self.circuit
            self.circuit = pcvl.Circuit(len(self.photons)+6)
            self.circuit.add(0, temp, merge=True)
        else:
            self.circuit = pcvl.Circuit(6, name=name)
        
        q0 = Qbit(len(self.photons), logical=False)
        q1 = Qbit(len(self.photons)+2, logical=False)
        q2 = Qbit(len(self.photons)+4, logical=False)

        q0.id = q0_id
        q1.id = q1_id
        q2.id = q2_id

        self.photons+=[*q0.get_photons(), *q1.get_photons(), *q2.get_photons()]
        self.qbits+=[q0, q1, q2]
    
        return q0, q1, q2

    def calc_in_state(self):
        """Calculate the input state iterating on all the single photonic lines input state.
        """
        in_state = [None]*len(self.photons)
        self.nph = 0
        for p in self.photons:
                assert p.in_state != None, "Photon was not initialized correctly"
                in_state[p.pos] = p.in_state
                self.nph += p.in_state
        self.in_state = in_state
    
    def calc_in_graph_state_ghz_only(self):
        """TODO: Do we assume the very first qubit to be a single |+> or should it also be a three qubit GHZ?"""
        G = nx.Graph()
        G.add_nodes_from(range(int(len(self.photons)/2)))
        for i in range(1,int(len(self.photons)/2),3):
            G.add_edge(i,i+1)
            G.add_edge(i+1,i+2)
        generator = StateGenerator(Encoding.DUAL_RAIL)
        return generator.graph_state(G)

    def fuse(self, q1:Qbit, q2:Qbit):
        """Perform fusion of type 1 on the qubit q1 and q2, witnessing the qubit q1.

        :param q1:
        :type q1: Qbit
        :param q2:
        :type q2: Qbit
        """
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
        """Performs fusion of type 2 on qubits q1 and q2.

        :param q1:
        :type q1: Qbit
        :param q2:
        :type q2: Qbit
        """
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
    
    def fuse75_generic(self, q1: Qbit, q2: Qbit):
        #assumes for each qubit the 0 mode (pH) is before the 1 (pV) and the two qubits are not intertwined
        newsize = self.circuit.m+4
        new_circ = pcvl.Circuit(m=newsize, name=self.circuit.name)
        new_circ.add(0,self.circuit)
        self.circuit = new_circ
        if q1.pH.pos < q2.pH.pos:
            aPos = q1.pH.pos
            bPos = q1.pV.pos
            cPos = q2.pH.pos
            dPos = q2.pV.pos
        else:
            aPos = q2.pH.pos
            bPos = q2.pV.pos
            cPos = q1.pH.pos
            dPos = q1.pV.pos
        print("positions A",aPos,"B",bPos,"C",cPos,"D",dPos)
        #outer loop 1
        print("sink B",bPos,"to D",dPos-1)
        for i in range(bPos, dPos-1): #sink B
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True)
        self.circuit.add((dPos-1,dPos), symb.BS.H()) #interact BD
        print("sink B",dPos,"to ancillas",newsize-5)
        for i in range(dPos, newsize-5): #sink B
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True)
        self.circuit.add((newsize-4,newsize-3), symb.BS.H()) #generate 20 02 states
        self.circuit.add((newsize-2,newsize-1), symb.BS.H())
        #outer loop 2
        print("sink A",aPos,"to C",cPos-2)
        for i in range(aPos, cPos-2): #sink A
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True)
        self.circuit.add((cPos-2,cPos-1), symb.BS.H()) #interact AC
        for i in range(cPos-1, newsize-6): #sink A
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True)
        for i in range(newsize-5, newsize-2): #sink B
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True)
        #outer loop 3
        for i in range(dPos-2, newsize-7): #sink D
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True)
        for i in range(newsize-6, newsize-4): #sink A
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True)
        #outer loop 4
        for i in range(cPos-2, newsize-8): #sink C
            self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True) 
        self.circuit.add((i, i+1), symb.BS.H(np.pi), merge=True) #sink A
        #outer loop 5
        for i in range(newsize-8, newsize-2, 2):
            self.circuit.add((i,i+1), symb.BS.H()) #interact with ancillas
        
        # return new_circ
        



    def fuse_2_75(self, q1:Qbit, q2:Qbit, a1: Qbit, a2: Qbit):
        #assuming q1 and q2 are next to each other as are ancilla1 and ancilla2
        posq1 = q1.pH.pos
        posq2 = q2.pH.pos
        posa1 = a1.pH.pos
        posa2 = a2.pH.pos
        # if q1.pH.pos > q2.pH.pos:
        #     pos1 = q2.pH.pos
        #     pos2 = q1.pH.pos
        # else:
        #     pos1 = q1.pH.pos
        #     pos2 = q2.pH.pos
        self.circuit.add((posa1,posa1+1), symb.BS.H())
        self.circuit.add((posa2,posa2+1), symb.BS.H())
        
        #interaction (A,B) with (C,D)
        self.circuit.add((posq1+1,posq2), symb.BS.H(np.pi))
        self.circuit.add((posq1,posq1+1), symb.BS.H())
        self.circuit.add((posq2,posq2+1), symb.BS.H())
        self.circuit.add((posq1+1,posq2), symb.BS.H(np.pi))
        
        #sinks
        self.sink(q2,a1)
        #sink directly above
        # self.circuit.add(posq1,pcvl.PERM(list(range(1,a1.pH.pos-1))+[0]))
        # self.circuit.add(posq1,pcvl.PERM(list(range(1,a1.pH.pos-1))+[0]))
        for i in range(posq1, a1.pH.pos-1):
            self.swap_photons(i, i+1)
        for i in range(posq1, a1.pH.pos-1):
            self.swap_photons(i, i+1)

        cell1_start = a1.pH.pos-2
        cell2_start = a1.pH.pos+2
        
        self.circuit.add((cell1_start+1,cell1_start+2), symb.BS.H(np.pi))
        self.circuit.add((cell1_start,cell1_start+1), symb.BS.H())
        self.circuit.add((cell1_start+2,cell1_start+3), symb.BS.H())
        self.circuit.add((cell1_start+1,cell1_start+2), symb.BS.H(np.pi))

        self.circuit.add((cell2_start+1,cell2_start+2), symb.BS.H(np.pi))
        self.circuit.add((cell2_start,cell2_start+1), symb.BS.H())
        self.circuit.add((cell2_start+2,cell2_start+3), symb.BS.H())
        self.circuit.add((cell2_start+1,cell2_start+2), symb.BS.H(np.pi))

        return cell1_start
    
    def get_75_fusion_post_select_states(self, instate, ancilla_pos_start):
        #assuming all 8 ancilla modes are next to each other 
        filter_bells = {'psi-': [], 'psi+': [], 'phi+': [], 'phi-': []}
        s_idx = ancilla_pos_start
        for state in pcvl.statevector.allstate_iterator(instate):
            if sum_modes(state, s_idx, s_idx + 4) == 3 and sum_modes(state, s_idx + 4, s_idx + 8) == 3:
                # psi - 
                filter_bells['psi-'].append(state)
            elif sum_modes(state, s_idx, s_idx + 4) == 4 and sum_modes(state, s_idx + 4, s_idx + 8) == 2:
                if (state[s_idx]+state[s_idx+2]) % 2 == 1:
                    #psi +
                    filter_bells['psi+'].append(state)
                else:
                    if (state[s_idx]+state[s_idx+2]) == 2:
                        if (state[s_idx]+state[s_idx+1]) % 2 == 0:
                            filter_bells['phi+'].append(state)
                        else:
                            filter_bells['phi-'].append(state)

            elif sum_modes(state, s_idx + 4, s_idx + 8) == 4 and sum_modes(state,s_idx, s_idx + 4) == 2:
                if (state[s_idx+4]+state[s_idx+6]) % 2 == 1:
                    #psi +
                    filter_bells['psi+'].append(state)
                else:
                    if (state[s_idx+4]+state[s_idx+6]) == 2:
                        if (state[s_idx+4]+state[s_idx+5]) % 2 == 0:
                            filter_bells['phi+'].append(state)
                        else:
                            filter_bells['phi-'].append(state)
        
        return filter_bells



    def post_select_type2_75(self, instate, ancilla_start):
        #assuming we measure ancillas from ancilla_start to end of circuit
        backend = pcvl.backends.NaiveBackend()
        backend.set_circuit(self.circuit)
        sum_probs = 0
        sim = pcvl.simulators.Simulator(backend)
        for bell_state, post_selected_state in prefilter_type2_75_options(self.get_75_fusion_post_select_states(instate, ancilla_start), ancilla_start).items():
            print('\n\n',bell_state,'\n\n')
            prob = {}
            for outstate in post_selected_state:
                if str(outstate[ancilla_start:]) not in prob:
                    prob[str(outstate[ancilla_start:])] = {}
                
                probamp = sim.prob_amplitude(instate,pcvl.BasicState(str(outstate)))
                sum_probs += abs(probamp)**2
                # print("test ",outstate,"amplitude",probamp)
                if abs(probamp)**2 > 10e-10:
                    if str(outstate[:ancilla_start]) not in prob[str(outstate[ancilla_start:])]:
                        prob[str(outstate[ancilla_start:])][str(outstate[:ancilla_start])] = []
                    prob[str(outstate[ancilla_start:])][str(outstate[:ancilla_start])].append(probamp)
                    # print("add to ",prob[str(outstate[ancilla_start:])][str(outstate[:ancilla_start])],probamp) #debug
          
            keys = []
            for p in prob.keys():
                if prob[p] == {}:
                    keys.append(p)
            for k in keys:
                del prob[k]
        
            pprint(prob)
        
        return sum_probs
        
    def calc_out_states(self, logical, witness):
        """Calculate all the possible out states generating all the possibles partitions of nph photons distribuited over the photonic lines.

        :param logical: add the output state to the list of possible out states only if it corresponds to a logical state.
        :type logical: bool
        :param witness: add the output state to the list of possible out states only if the WITNESS photons are witnessed accordingly.
        :type witness: bool
        """
        self.out_states = []
        if logical or witness:
            for l in partition(self.nph, len(self.photons)):
                if check(self.photons, l, logical=logical, witness=witness):
                    self.out_states.append(l)
        else:
            for l in partition(self.nph, len(self.photons)):
                self.out_states.append(l)

    def get_run_results(self, logical=False, witness=False):
        results = []
        self.calc_out_states(logical, witness)
        for o in self.out_states:
            p = self.ampli(self.in_state, o)
            if(abs(p) > 10e-10):
                results.append((o,p))
        return results

    def run(self, logical=True, witness=True):
        """Print the amplitudes of the output state.

        :param logical: if True, checks only logical output states, defaults to True
        :type logical: bool, optional
        :param witness: _if True, checks only output states where WITNESS photons are witnessed accordingly, defaults to True
        :type witness: bool, optional
        """
        self.calc_out_states(logical, witness)
        for o in self.out_states:
            p = self.ampli(self.in_state, o)
            if(abs(p) > 10e-10):
                print(o)
                print(p)

    def run_format(self):
        """Smart function to check only logical output states.
        """
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
        """Perceval built-in function to calculate amplitudes"""
        backend = pcvl.backends.NaiveBackend()
        backend.set_circuit(self.circuit)
        backend.set_input_state(pcvl.BasicState(in_state))
        # for old perceval versions:
        # backend = pcvl.BackendFactory.get_backend(backend)
        # sim = backend(self.circuit)
        # return(sim.probampli_be(input_state=pcvl.BasicState(in_state), output_state = pcvl.BasicState(out_state)))
        return(backend.prob_amplitude(pcvl.BasicState(out_state)))

    def loopify(self, display = True):
        """Function to rewrite the circuit in a format where the optical elements are divided accordingly to the corresponding outer loop they are performed in.

        :param display: if True, it adds graphical barriers to the Perceval circuit. It just makes the displaying more clear, defaults to True
        :type display: bool, optional
        :return: last[i] is the last optical element on the photonic line of index i, depth[i] is the outer loop number corresponding to last[i]
        :rtype: list, list
        """
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

def sum_modes(state, start, end):
    res = 0
    for i in range(start, end):
        res += state[i]
    return res

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

def prefilter_type2_75_options(filter_bells, ancilla_pos_start):
    """Prefilter postselection states according to whether we have correct photon numbers in remaining qubits
    this cannot be done in practice"""
    res = {'psi-': [], 'psi+': [], 'phi+': [], 'phi-': []}
    for k,v in filter_bells.items():
        for state in v:
            not_valid = False
            for i in range(0,ancilla_pos_start,2):
                if state[i] + state[i+1] > 1:
                    not_valid = True
                    break
            if not not_valid:
                res[k].append(state)
    return res