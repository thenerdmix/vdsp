from enum import Enum
import itertools

class PhotonType(Enum):
    """There are three possible types of photons. 1) Photons that belong to a qubit (COMPutational photons), 2) Photons that will be witnessed (WITNESS), 3) Everything else.
    Photons of type COMP will always have a corresponding Qbit object and a corresponding polariation Horizontal or Vertical.
    Photon of type WITNESS will always have a out_state.
    """
    COMP = "COMP"
    WITNESS = "WITNESS"
    NONE = "99"

    def __str__(self):
        return self.name

class Photon(object):
    newid = itertools.count()
    """A photonic line.

    :param id: the id of the photon
    :type id: int
    :param pos: the position of the photon in the photonic circuit. By default the position is initialized as the photon id.
    :type pos: int
    :param type: the photon can be a computational or a witness photon
    :type type: PhotonType
    :param in_state: how many photons there are in this specific photonic line as input
    :type in_state: int
    :param out_state: if this line must be witnessed, how many photons I expect to observe in this specific line.
    :type out_state: int
    :param qubit: if this line is computational, the Qbit object corresponding to this photonic line
    :type qubit: Qbit object
    :param polarization: if this line is computational, it can correspond either to an horizontally polarized photon or a vertical polarized one.
    """

    def __init__(self, type: PhotonType):
        self.id = next(Photon.newid)
        self.pos = self.id
        self.type = type
        self.in_state = None
        self.out_state = None

        self.qubit = None
        self.polarization = None

    def set_in_state(self, in_state):
        """Set the in state of the circuit. It must be a Fock state represented by the in_state list.

        :param in_state: a list of int representing how many photons there are in each photonic line.
        :type in_state: list of int
        """
        self.in_state = in_state

    def set_pos(self, pos):
        self.pos = pos

    def set_witness(self, out_state):
        """Set a specific photonic line to be witnessed, with expected number of photons equal to out_state.

        :param out_state: how many photons must be witnessed in this specific line.
        :type out_state: int
        """
        self.type = PhotonType.WITNESS
        self.out_state =  out_state
        self.qubit = None

    def other(self):
        """If a Photon object corresponds to a logical Qbit, returns the other Photon object corresponding to the same Qbit.

        :return: Photon object
        :rtype: Photon object
        """
        assert self.type == PhotonType.COMP, "Trying to get the other photon of a non COMP photon"
        if self.polarization==PhotonPolarization.H:
            return self.qubit.pV
        elif self.polarization==PhotonPolarization.V:
            return self.qubit.pH
        else:
            assert True, "Polarization not set properly!"


class PhotonPolarization(Enum):
    """Photons of type COMP in the dual rail enconding can either correspond to the Horizontal or Vertical polarization in the polarization enconding.
    """
    H = "H"
    V = "V"
    NONE = "99"


class Qbit(object):
    """The Qbit object represents a logical qubit. A logical qubit in the dual rail encoding is just the set of tho photons: one of polarization Horizontal and the other of polarization Vertical.

    :param pH: the horizontal Photon object
    :type object: Photon
    :param pV: the vertical Photon object. Its default position in the photonic circuit is just the position of the horizontally polarized photon +1.
    :type object: Photon
    """
    newid = itertools.count()

    def __init__(self, pos, logical=False):
        """Constructor method.

        :param pos: the position of the horizontally polarized photon.
        :type pos: int
        :param logical: the logical value of the qubit, defaults to False
        :type logical: bool, optional
        """
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
        """Returns the two photons corresponding to the logical qubit.

        :return: a list of two photons
        :rtype: list of Photon objects
        """
        return [self.pH, self.pV]
    

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


def format_logical(qbits, state):
    """Given a set of qubits and a state state, it returns a dictionary mapping every qubit to the corresponding logical state.

    :param qbits: list of qubits
    :type qbits: list of Qbit
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
    :type qbits: list of Qbit
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

