
from engine.quantum_engine import make_basic_circuit, run_circuit_counts

def deutsch_jozsa_circuit(n_qubits, oracle_type='constant_zero'):
    if n_qubits < 1: n_qubits = 1
    steps = [('H',0)]
    if oracle_type == 'balanced_parity':
        steps.append(('X',0))
    steps.append(('H',0))
    return make_basic_circuit(1, steps, measure=True)

def grover_circuit(n_qubits, marked_state='01', iterations=1):
    steps = []
    for i in range(n_qubits):
        steps.append(('H', i))
    for idx, b in enumerate(reversed(marked_state)):
        if b == '0':
            steps.append(('X', idx))
    if n_qubits == 2:
        steps.append(('H', 1)); steps.append(('CNOT',(0,1))); steps.append(('H',1))
    for idx, b in enumerate(reversed(marked_state)):
        if b == '0':
            steps.append(('X', idx))
    # diffusion approx
    for i in range(n_qubits): steps.append(('H', i))
    for i in range(n_qubits): steps.append(('X', i))
    if n_qubits == 2:
        steps.append(('H', 1)); steps.append(('CNOT',(0,1))); steps.append(('H',1))
    for i in range(n_qubits): steps.append(('X', i))
    for i in range(n_qubits): steps.append(('H', i))
    return make_basic_circuit(n_qubits, steps, measure=True)

def _prepare_state_steps(state_key):
    if state_key == 'zero': return []
    if state_key == 'one': return [('X',0)]
    if state_key == 'plus': return [('H',0)]
    if state_key == 'minus': return [('X',0),('H',0)]
    return [('H',0)]

def teleportation_sample_measure(state_key='plus', shots=1):
    steps = []
    steps += _prepare_state_steps(state_key)
    steps.append(('H',1)); steps.append(('CNOT',(1,2)))
    steps.append(('CNOT',(0,1))); steps.append(('H',0))
    circ = make_basic_circuit(3, steps, measure=True)
    counts = run_circuit_counts(circ, shots=shots)
    # extract q0 and q1 bits (q0..q2 order)
    pair_counts = {}
    for k,v in counts.items():
        q0 = k[0]; q1 = k[1]; pair = q1+q0
        pair_counts[pair] = pair_counts.get(pair,0)+v
    if not pair_counts:
        return None, counts
    outcome = max(pair_counts.items(), key=lambda kv: kv[1])[0]
    return outcome, pair_counts

def teleportation_apply_correction_and_measure(m0, m1, state_key='plus', shots=256):
    steps = []
    steps += _prepare_state_steps(state_key)
    steps.append(('H',1)); steps.append(('CNOT',(1,2)))
    steps.append(('CNOT',(0,1))); steps.append(('H',0))
    if m1 == 1: steps.append(('X',2))
    if m0 == 1: steps.append(('Z',2))
    circ = make_basic_circuit(3, steps, measure=True)
    counts = run_circuit_counts(circ, shots=shots)
    simplified = {}
    for k,v in counts.items():
        bit = k[2]; simplified[bit] = simplified.get(bit,0)+v
    return simplified
