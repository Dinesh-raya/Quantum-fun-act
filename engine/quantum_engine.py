
from engine.qsim import init_state, apply_operator_sequence, measure_counts

def make_basic_circuit(n_qubits, steps, measure=False):
    return (n_qubits, steps, measure)

def run_circuit_counts(circuit_repr, shots=512):
    n_qubits, steps, measure = circuit_repr
    state = init_state(n_qubits)
    final = apply_operator_sequence(n_qubits, state, steps)
    if measure:
        return measure_counts(final, n_qubits, shots=shots)
    else:
        probs = (abs(final)**2).tolist()
        return {format(i, '0{}b'.format(n_qubits)): int(round(p*shots)) for i,p in enumerate(probs)}
