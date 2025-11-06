
import streamlit as st, json
from core.game_state import init_state, award_xp, award_badge
from engine.quantum_engine import make_basic_circuit, run_circuit_counts
from engine import algorithms
from ui.visualizer import plot_counts_figure

st.set_page_config(page_title='Quantum Coins v4', layout='centered')
st.title('Quantum Coins — Version 4 (Qiskit-free)')

init_state(st.session_state)

st.sidebar.header('Progress')
st.sidebar.write(f"XP: {st.session_state.xp}")
st.sidebar.write('Badges:')
for b in st.session_state.badges: st.sidebar.write('-', b)

demo = st.selectbox('Demo', ['Teleportation','Deutsch-Jozsa','Grover','Bell Pair'])

if demo == 'Teleportation':
    st.header('Teleportation')
    state_choice = st.selectbox('State to teleport', ['plus','zero','one','minus'])
    if st.button('Auto-Demo Teleportation'):
        outcome, _ = algorithms.teleportation_sample_measure(state_key=state_choice, shots=1)
        if outcome is None:
            st.error('Teleportation sampling failed.')
        else:
            try:
                m0 = int(outcome[-1]); m1 = int(outcome[-2]) if len(outcome)>=2 else 0
            except Exception:
                m0=0; m1=0
            corrected = algorithms.teleportation_apply_correction_and_measure(m0=m0, m1=m1, state_key=state_choice, shots=512)
            st.pyplot(plot_counts_figure(corrected))
            st.success('Auto-demo complete.')
            award_xp(st.session_state, 30)
            award_badge(st.session_state, 'Teleportation Observer')

elif demo == 'Deutsch-Jozsa':
    st.header('Deutsch-Jozsa')
    qc = algorithms.deutsch_jozsa_circuit(1, oracle_type='balanced_parity')
    counts = run_circuit_counts(qc, shots=512)
    st.pyplot(plot_counts_figure(counts))

elif demo == 'Grover':
    st.header('Grover (2-qubit)')
    qc = algorithms.grover_circuit(2, marked_state='01', iterations=1)
    counts = run_circuit_counts(qc, shots=512)
    st.pyplot(plot_counts_figure(counts))

elif demo == 'Bell Pair':
    st.header('Bell Pair')
    circ = make_basic_circuit(2, [('H',0), ('CNOT',(0,1))], measure=True)
    counts = run_circuit_counts(circ, shots=512)
    st.pyplot(plot_counts_figure(counts))
    if counts.get('00',0) + counts.get('11',0) > 0:
        award_xp(st.session_state, 20)
        award_badge(st.session_state, 'Bell Buddy')

st.markdown('---')
if st.button('Save progress'):
    data = {'xp': st.session_state.xp, 'badges': st.session_state.badges, 'campaign_progress': st.session_state.campaign_progress}
    st.download_button('Download progress JSON', data=json.dumps(data), file_name='progress_v4.json')
