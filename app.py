
import streamlit as st
import base64, os, json
from engine.quantum_engine import run_circuit_counts, make_basic_circuit
from engine import puzzles, algorithms
from ui.visualizer import plot_counts_figure, plot_bloch_plotly

st.set_page_config(page_title='Quantum Coins', layout='centered')

# --- Styles & animations ---
st.markdown("""
<style>
.card { padding:12px; border-radius:10px; background: linear-gradient(180deg,#ffffff,#f0f8ff); margin-bottom:8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);}
.small { font-size:14px; color:#333; }
.center { display:flex; align-items:center; }
.spinny-anim { animation: spin 2s linear infinite; transform-origin: 50% 50%; }
@keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
.level-map { display:flex; gap:10px; align-items:center; }
.level-box { padding:8px 12px; border-radius:8px; background:#eef; border:1px solid #ccd; }
.locked { opacity:0.45; filter:grayscale(60%); }
.xp-bar { height:18px; background:#ddd; border-radius:9px; overflow:hidden; }
.xp-fill { height:100%; background:linear-gradient(90deg,#FFD966,#F4B400); border-radius:9px; }
</style>
""", unsafe_allow_html=True)

st.title('Quantum Coins — Adventure Map 🪙✨')

# Initialize session state variables
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'campaign_progress' not in st.session_state:
    st.session_state.campaign_progress = 0
if 'circuit_steps' not in st.session_state:
    st.session_state.circuit_steps = []
if 'tele_stage' not in st.session_state:
    st.session_state.tele_stage = 'idle'  # idle, prepared, measured, corrected

# Helper functions
def award_xp(amount):
    st.session_state.xp += amount

def award_badge(name):
    if name not in st.session_state.badges:
        st.session_state.badges.append(name)
        st.success(f'Badge earned: {name} 🎖️')

# Load SVGs for characters as base64 to inline
def svg_to_datauri(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    b64 = base64.b64encode(raw.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

spinny_uri = svg_to_datauri(os.path.join('assets','spinny.svg'))
tango_uri = svg_to_datauri(os.path.join('assets','tango.svg'))
grov_uri = svg_to_datauri(os.path.join('assets','grov.svg'))
bitty_uri = svg_to_datauri(os.path.join('assets','bitty.svg'))

# Top bar: XP and badges
st.sidebar.markdown('**XP:** ' + str(st.session_state.xp))
st.sidebar.markdown('**Badges:**')
if st.session_state.badges:
    for b in st.session_state.badges:
        st.sidebar.markdown(f'- {b}')
else:
    st.sidebar.markdown('_No badges yet_')

# Adventure Map with unlocks
st.header('Adventure Map — Levels')
levels = list(puzzles.PUZZLES.keys())
cols = st.columns(len(levels))
for i, lvl in enumerate(levels):
    with cols[i]:
        locked = (i > st.session_state.campaign_progress)
        cls = 'level-box locked' if locked else 'level-box'
        st.markdown(f"<div class='{cls}'>{i+1}. {lvl.split(' - ')[1]}</div>", unsafe_allow_html=True)

# Display Spinny in header
st.markdown(f"<div class='card center'><img src='{spinny_uri}' width='80' class='spinny-anim' style='margin-right:12px'/> <div><b>Welcome, explorer!</b><div class='small'>Collect XP to unlock levels and meet all characters!</div></div></div>", unsafe_allow_html=True)

# Mode selector
mode = st.selectbox('Mode', ['Campaign','Sandbox','Tutorial'])

# Campaign controls: choose unlocked level
if mode == 'Campaign':
    lvl_idx = st.slider('Choose unlocked level', 0, st.session_state.campaign_progress, 0)
else:
    lvl_idx = st.selectbox('Choose level', range(len(levels)), index=0)
level_name = levels[lvl_idx]

st.markdown(f"<div class='card'><b>{level_name}</b><div class='small'>{puzzles.PUZZLES[level_name].get('story','')}</div></div>", unsafe_allow_html=True)

# Simple circuit builder area (reused from previous app)
st.subheader('Build spells (gates)')
expected_qubits = puzzles.PUZZLES[level_name]['qubits']
qubits = expected_qubits
cols = st.columns(6)
if cols[0].button('H (Spin)'):
    st.session_state.circuit_steps.append(('H', 0))
if cols[1].button('X (Flip)'):
    st.session_state.circuit_steps.append(('X', 0))
if cols[2].button('Z (Zap)'):
    st.session_state.circuit_steps.append(('Z', 0))
if cols[3].button('S (Soft)'):
    st.session_state.circuit_steps.append(('S', 0))
if cols[4].button('T (Tiny)'):
    st.session_state.circuit_steps.append(('T', 0))
if cols[5].button('RY (Tilt)'):
    st.session_state.circuit_steps.append(('RY', 0.9))
cnot_col = st.columns(2)
if cnot_col[0].button('CNOT (Link)') and expected_qubits >= 2:
    st.session_state.circuit_steps.append(('CNOT', (0,1)))
if st.button('Clear spells'):
    st.session_state.circuit_steps = []
st.write('Spells:', st.session_state.circuit_steps)

shots = st.slider('Shots', 64, 2048, 512, step=64)
if st.button('Run spells'):
    qc = make_basic_circuit(qubits, st.session_state.circuit_steps, measure=True)
    counts = run_circuit_counts(qc, shots=shots)
    st.session_state.last_counts = counts
    st.success('Magic ran! Check results below.')
    # award XP for trying things
    award_xp(5)

# Show results and evaluate puzzles in campaign
if 'last_counts' in st.session_state:
    st.subheader('Results')
    st.pyplot(plot_counts_figure(st.session_state.last_counts))
    st.write(st.session_state.last_counts)
    if mode == 'Campaign':
        ok, reason = puzzles.check_puzzle_success(level_name, qubits, st.session_state.last_counts)
        if ok:
            st.success('Level success! ' + reason)
            award_xp(20)
            # award badges per level
            if 'Teleport' in level_name:
                award_badge('Teleportation Wizard')
            idx = lvl_idx
            if idx >= st.session_state.campaign_progress:
                st.session_state.campaign_progress = min(len(levels)-1, idx+1)

# Animated Teleportation Mini-Game (detailed scene flow)
st.markdown('---')
st.header('Teleportation Mini-Game 🎯')
st.markdown("""<div class='small'>Play through the teleportation scene: prepare a state, make Alice measure, send bits, apply corrections, and watch Bob get the state!</div>""", unsafe_allow_html=True)

# Scene controls
scene = st.session_state.get('tele_stage','idle')
colA, colB = st.columns([2,1])
with colA:
    state_choice = st.selectbox('Choose a state to send', ['plus','zero','one','minus'], index=0)
    if st.button('1) Alice: Prepare & Entangle'):
        # prepare and entangle but don't measure yet; set stage
        st.session_state.tele_stage = 'prepared'
        st.success('Alice prepared the state and created an entangled pair with Bob.')
    if st.session_state.tele_stage == 'prepared' and st.button('2) Alice: Measure now'):
        # run sample measurement to get a single outcome
        outcome, base_counts = algorithms.teleportation_sample_measure(state_key=state_choice, shots=1)
        if outcome is None:
            st.error('Measurement failed.')
        else:
            st.session_state.tele_outcome = outcome  # store classical bits string
            st.session_state.tele_stage = 'measured'
            st.success(f'Alice measured bits (classical): {outcome}')
    if st.session_state.tele_stage == 'measured':
        st.write('Measured bits (classical):', st.session_state.tele_outcome)
        # Show player the bit values
        try:
            m0 = int(st.session_state.tele_outcome[-1])
            m1 = int(st.session_state.tele_outcome[-2]) if len(st.session_state.tele_outcome)>=2 else 0
        except Exception:
            m0=0; m1=0
        st.write(f'm1 = {m1}, m0 = {m0}')
        st.info('Now choose which corrections Bob should apply. Try to guess!')
        corr_col1, corr_col2, corr_col3 = st.columns(3)
        if corr_col1.button('Apply X'):
            chosen = (1,0)
        elif corr_col2.button('Apply Z'):
            chosen = (0,1)
        elif corr_col3.button('Apply X and Z'):
            chosen = (1,1)
        elif st.button('No correction'):
            chosen = (0,0)
        else:
            chosen = None
        if chosen is not None:
            m1_guess, m0_guess = chosen
            corrected = algorithms.teleportation_apply_correction_and_measure(m0=m0_guess, m1=m1_guess, state_key=state_choice, shots=256)
            st.session_state.last_counts = corrected
            st.session_state.last_qubits = 1
            # Evaluate success heuristically
            success = False
            if state_choice == 'zero':
                success = corrected.get('0',0) > corrected.get('1',0)
            elif state_choice == 'one':
                success = corrected.get('1',0) > corrected.get('0',0)
            elif state_choice == 'plus':
                total = sum(corrected.values()) if corrected else 1
                p0 = corrected.get('0',0)/total
                success = abs(p0 - 0.5) < 0.35
            else:
                success = True
            if success:
                st.balloons()
                st.success('Teleportation successful! Bob received the state.')
                award_xp(50)
                award_badge('Teleportation Hero')
                st.session_state.tele_stage = 'corrected'
            else:
                st.error('Not quite — try a different correction or use Auto-Demo.')
    if st.button('Auto-Demo: Show correct correction'):
        outcome, _ = algorithms.teleportation_sample_measure(state_key=state_choice, shots=1)
        try:
            m0 = int(outcome[-1]); m1 = int(outcome[-2]) if len(outcome)>=2 else 0
        except Exception:
            m0=0; m1=0
        corrected = algorithms.teleportation_apply_correction_and_measure(m0=m0, m1=m1, state_key=state_choice, shots=256)
        st.session_state.last_counts = corrected
        st.session_state.last_qubits = 1
        st.success('Auto-demo applied correct corrections — Bob receives the state!')
        award_xp(30)
        award_badge('Teleportation Observer')
with colB:
    # Show characters and a tiny storyboard
    st.image(spinny_uri, width=140)
    st.image(tango_uri, width=200)
    st.image(grov_uri, width=120)
    st.image(bitty_uri, width=120)

# XP progress bar visualization and level unlock thresholds
st.markdown('---')
st.header('Progress & Rewards')
xp = st.session_state.xp
# define thresholds: each level requires 50 xp to unlock next (configurable)
thresholds = [0,50,100,150,200,250,300,350]
# compute fill percentage for next unlock
next_idx = min(len(thresholds)-1, st.session_state.campaign_progress+1)
need = thresholds[next_idx] - xp
pct = min(1.0, xp / thresholds[next_idx]) if thresholds[next_idx] > 0 else 1.0
st.markdown('<div class="xp-bar"><div class="xp-fill" style="width: {}%"></div></div>'.format(int(pct*100)), unsafe_allow_html=True)
st.write(f'XP: {xp} — Next unlock in {max(0, need)} XP')

# Save/Load progress
st.markdown('---')
st.write('Save / Load Progress')
if st.button('Save progress'):
    data = {'xp': st.session_state.xp, 'badges': st.session_state.badges, 'campaign_progress': st.session_state.campaign_progress}
    st.download_button('Download progress JSON', data=json.dumps(data), file_name='progress.json')
if st.button('Load progress from file'):
    uploaded = st.file_uploader('Upload progress JSON', type=['json'])
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            st.session_state.xp = data.get('xp', st.session_state.xp)
            st.session_state.badges = data.get('badges', st.session_state.badges)
            st.session_state.campaign_progress = data.get('campaign_progress', st.session_state.campaign_progress)
            st.success('Progress loaded.')
        except Exception as e:
            st.error('Failed to load file: ' + str(e))

st.markdown('---')
st.markdown('Built with ❤️ — play and learn!')
