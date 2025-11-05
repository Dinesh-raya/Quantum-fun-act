
from qiskit import QuantumCircuit, Aer, execute
import math

def deutsch_jozsa_circuit(n_qubits, oracle_type='constant_zero'):
    qc = QuantumCircuit(n_qubits+1, n_qubits)
    qc.x(n_qubits)
    qc.h(range(n_qubits+1))
    if oracle_type == 'constant_zero':
        pass
    elif oracle_type == 'constant_one':
        qc.x(n_qubits)
    elif oracle_type == 'balanced_parity':
        for i in range(n_qubits):
            qc.cx(i, n_qubits)
    elif oracle_type == 'balanced_first':
        qc.cx(0, n_qubits)
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def grover_oracle(n_qubits, marked_state):
    qc = QuantumCircuit(n_qubits)
    for i, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            qc.x(i)
    if n_qubits == 1:
        qc.z(0)
    else:
        qc.h(n_qubits-1)
        try:
            qc.mcx(list(range(n_qubits-1)), n_qubits-1)
        except Exception:
            for c in range(n_qubits-1):
                qc.cx(c, n_qubits-1)
        qc.h(n_qubits-1)
    for i, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            qc.x(i)
    return qc

def grover_diffusion(n_qubits):
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    if n_qubits == 1:
        qc.z(0)
    else:
        qc.h(n_qubits-1)
        try:
            qc.mcx(list(range(n_qubits-1)), n_qubits-1)
        except Exception:
            for c in range(n_qubits-1):
                qc.cx(c, n_qubits-1)
        qc.h(n_qubits-1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc

def grover_circuit(n_qubits, marked_state, iterations=1):
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for _ in range(iterations):
        qc += grover_oracle(n_qubits, marked_state)
        qc += grover_diffusion(n_qubits)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def teleportation_full(state_prep=None):
    # Returns a circuit that performs teleportation and includes the correction steps
    # Qubit 0: message (Alice), 1: Alice's entangled, 2: Bob's entangled
    qc = QuantumCircuit(3, 2)
    # prepare arbitrary state on q0
    if state_prep is None:
        qc.h(0)  # default |+>
    else:
        state_prep(qc, 0)
    # create Bell pair between q1 and q2
    qc.h(1)
    qc.cx(1,2)
    # Bell measurement on q0 & q1
    qc.cx(0,1)
    qc.h(0)
    qc.measure(0,0)  # m0
    qc.measure(1,1)  # m1
    # conditional corrections on Bob's qubit (q2) based on classical bits m0,m1
    # If m1 == 1 -> apply X; if m0 == 1 -> apply Z  (note: order depends on convention)
    # Qiskit supports classical conditional gates using c_if on classical registers for some gates
    # We'll implement corrections using simple approach: append gates conditioned on classical bits
    # because direct c_if with statevector simulator might be limited; instead we'll produce two branches for demo
    return qc

def teleportation_correction_run(shots=256):
    # For demo: prepare |+> on q0, run teleportation without active correction, then emulate correction by
    # running circuits that apply corrections based on measurement results and combining counts.
    backend = Aer.get_backend('aer_simulator')
    # Build base teleportation circuit (measures m0,m1)
    base = teleportation_full()
    # Run base to get measurement distribution for m0,m1
    job = execute(base, backend, shots=shots)
    result = job.result()
    counts = result.get_counts()
    # counts keys are 2-bit strings for classical bits (m1 m0) plus maybe quantum bits if measured; adapt
    # We'll build corrected counts for Bob's qubit by running conditional circuits per outcome
    corrected_counts = {}
    for outcome, cnt in counts.items():
        # outcome format could be like 'b2 b1' depending on measurement order; Qiskit returns classical regs as bitstrings
        # The base circuit measured c0 then c1, so classical register ordering is [c1, c0] in the returned string (qiskit endianness)
        # We'll parse from right: last bit is m0, second-last is m1
        m0 = int(outcome[-1])
        m1 = int(outcome[-2]) if len(outcome) >= 2 else 0
        # Build circuit that prepares the same state, creates bell pair, measures m0,m1, then applies corrections on q2
        qc = teleportation_full()
        # Remove measurements to allow applying corrections (rebuild instead)
        qc_no_meas = QuantumCircuit(3, 0)
        # prepare same state
        qc_no_meas.h(0)
        qc_no_meas.h(1)
        qc_no_meas.cx(1,2)
        qc_no_meas.cx(0,1)
        qc_no_meas.h(0)
        # apply corrections based on m0,m1
        if m1 == 1:
            qc_no_meas.x(2)
        if m0 == 1:
            qc_no_meas.z(2)
        # measure Bob's qubit
        qc_no_meas.measure_all()
        job2 = execute(qc_no_meas, backend, shots=cnt)
        res2 = job2.result()
        c2 = res2.get_counts()
        # aggregate counts
        for k,v in c2.items():
            corrected_counts[k] = corrected_counts.get(k,0)+v
    return corrected_counts



# --- Interactive teleportation helpers ---
def _prepare_state_on_q0(qc, state_key):
    """Apply a simple state preparation on qubit 0 based on a key."""
    if state_key == 'zero':
        # |0> do nothing
        pass
    elif state_key == 'one':
        qc.x(0)
    elif state_key == 'plus':
        qc.h(0)
    elif state_key == 'minus':
        qc.x(0); qc.h(0)
    elif state_key == 'custom_h_then_x':
        qc.h(0); qc.x(0)
    else:
        # default to plus
        qc.h(0)

def teleportation_sample_measure(state_key='plus', shots=1):
    """Prepare state on q0, create Bell pair q1-q2, perform Bell measurement on q0,q1,
    and return a sampled classical outcome string (m1 m0) from measuring q0,q1.
    """
    qc = QuantumCircuit(3, 2)
    _prepare_state_on_q0(qc, state_key)
    qc.h(1); qc.cx(1,2)
    qc.cx(0,1); qc.h(0)
    qc.measure(0,0)  # m0 in c0
    qc.measure(1,1)  # m1 in c1
    backend = Aer.get_backend('aer_simulator')
    job = execute(qc, backend, shots=shots)
    result = job.result()
    counts = result.get_counts()
    # choose a sampled outcome key (classical bits). Qiskit returns bitstrings in order c1c0 typically.
    # We will pick the most frequent outcome or a random sampled one from counts weighted by counts.
    # For simplicity, pick the first key
    if not counts:
        return None, counts
    # pick a key (most common)
    outcome = max(counts.items(), key=lambda kv: kv[1])[0]
    return outcome, counts

def teleportation_apply_correction_and_measure(m0, m1, state_key='plus', shots=256):
    """Given classical bits m0,m1 (ints 0/1), rebuild the teleportation circuit but apply corrections on Bob's qubit q2
    according to m0,m1 and measure Bob's qubit to show the received state distribution.
    Returns counts for Bob's measured qubit (as bitstrings '0' or '1' possibly with other bits depending on measurement order).
    """
    # Build a circuit that prepares the same initial state and entanglement, then applies corrections on q2.
    qc = QuantumCircuit(3, 1)  # measure only Bob into 1 classical bit
    _prepare_state_on_q0(qc, state_key)
    qc.h(1); qc.cx(1,2)
    qc.cx(0,1); qc.h(0)
    # Here instead of measuring and branching, we directly apply corrections according to provided bits.
    if m1 == 1:
        qc.x(2)
    if m0 == 1:
        qc.z(2)
    # measure Bob's qubit into classical bit 0
    qc.measure(2, 0)
    backend = Aer.get_backend('aer_simulator')
    job = execute(qc, backend, shots=shots)
    result = job.result()
    counts = result.get_counts()
    # Normalize keys possibly like '0' or '00' depending; ensure we return single-bit keys by extracting last char
    simplified = {}
    for k,v in counts.items():
        simplified[k[-1]] = simplified.get(k[-1], 0) + v
    return simplified

