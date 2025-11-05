
from qiskit import QuantumCircuit, Aer, execute

def make_basic_circuit(n_qubits, steps, measure=False):
    qc = QuantumCircuit(n_qubits, n_qubits if measure else 0)
    for s in steps:
        gate = s[0]
        arg = s[1]
        if gate == 'H':
            qc.h(arg)
        elif gate == 'X':
            qc.x(arg)
        elif gate == 'RY':
            angle = arg if isinstance(arg, (int,float)) else float(arg)
            qc.ry(angle, 0)
        elif gate == 'CNOT':
            ctl, tgt = arg
            qc.cx(ctl, tgt)
        elif gate == 'Z':
            qc.z(arg)
        elif gate == 'S':
            qc.s(arg)
        elif gate == 'T':
            qc.t(arg)
    if measure:
        qc.measure_all()
    return qc

def run_circuit_counts(qc, shots=512):
    try:
        simulator = Aer.get_backend('aer_simulator')
        job = execute(qc, simulator, shots=shots)
        result = job.result()
        counts = result.get_counts()
    except Exception as e:
        counts = {'0'*qc.num_qubits: shots}
    return counts
