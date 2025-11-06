
import numpy as np
from collections import Counter

H = (1/np.sqrt(2)) * np.array([[1,1],[1,-1]], dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)
S = np.array([[1,0],[0,1j]], dtype=complex)
T = np.array([[1,0],[0, np.exp(1j*np.pi/4)]], dtype=complex)

def RY(theta):
    import numpy as np
    return np.array([[np.cos(theta/2), -np.sin(theta/2)],[np.sin(theta/2), np.cos(theta/2)]], dtype=complex)

def kron_n(mats):
    import numpy as np
    res = np.array([1], dtype=complex)
    for m in mats:
        res = np.kron(res, m)
    return res

def apply_single(state, gate, target, n_qubits):
    import numpy as np
    ops = [np.eye(2, dtype=complex)] * n_qubits
    ops[target] = gate
    U = kron_n(ops)
    return U.dot(state)

def apply_cnot(state, control, target, n_qubits):
    import numpy as np
    dim = 2**n_qubits
    U = np.zeros((dim,dim), dtype=complex)
    for i in range(dim):
        bits = [(i>>k)&1 for k in reversed(range(n_qubits))]
        new_bits = bits.copy()
        if bits[control] == 1:
            new_bits[target] ^= 1
        j = 0
        for b in new_bits:
            j = (j<<1) | b
        U[j,i] = 1.0
    return U.dot(state)

def init_state(n_qubits):
    import numpy as np
    dim = 2**n_qubits
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0
    return state

def measure_counts(state, n_qubits, shots=512):
    import numpy as np
    probs = np.abs(state)**2
    outcomes = np.random.choice(len(probs), size=shots, p=probs)
    counts = Counter()
    for o in outcomes:
        bstr = format(o, '0{}b'.format(n_qubits))
        counts[bstr] += 1
    return dict(counts)

def apply_operator_sequence(n_qubits, state, steps):
    s = state.copy()
    for step in steps:
        g = step[0]; arg = step[1]
        if g == 'H':
            s = apply_single(s, H, arg, n_qubits)
        elif g == 'X':
            s = apply_single(s, X, arg, n_qubits)
        elif g == 'Y':
            s = apply_single(s, Y, arg, n_qubits)
        elif g == 'Z':
            s = apply_single(s, Z, arg, n_qubits)
        elif g == 'S':
            s = apply_single(s, S, arg, n_qubits)
        elif g == 'T':
            s = apply_single(s, T, arg, n_qubits)
        elif g == 'RY':
            theta = arg[0] if isinstance(arg, (list,tuple)) else arg
            target = arg[1] if isinstance(arg, (list,tuple)) else 0
            s = apply_single(s, RY(theta), target, n_qubits)
        elif g in ('CNOT','CX'):
            ctl, tgt = arg
            s = apply_cnot(s, ctl, tgt, n_qubits)
    return s
