
# Expanded puzzle definitions with kid-friendly story dialogs and NPC lines
def _prob(counts, state):
    total = sum(counts.values()) if counts else 1
    return counts.get(state, 0) / total

PUZZLES = {
    'Level 1 - Spinny Warmup': {
        'qubits': 1,
        'goal': lambda counts: _prob(counts, '1') > 0.8,
        'explain': 'Spinny likes tails. Make the coin land on TAILS (1) more than 80% of the time.',
        'story': "Spinny is sleepy and prefers tails. Use the Flip spell to help him.",
        'hint': 'Try X (Flip) or RY (Tilt)'
    },
    'Level 2 - Flip Mountain': {
        'qubits': 1,
        'goal': lambda counts: _prob(counts, '0') > 0.8,
        'explain': 'Make Spinny love HEADS (0) most of the time. X flips the coin.',
        'story': "The mountain winds push Spinny to heads. Use a quick Flip!",
        'hint': 'Try X'
    },
    'Level 3 - Superposition Hill': {
        'qubits': 1,
        'goal': lambda counts: abs(_prob(counts,'0') - 0.5) < 0.15,
        'explain': 'Make the coin be BOTH heads and tails equally. Use the Spin spell (H).',
        'story': "Spinny loves to dance between both sides — spin him!" ,
        'hint': 'Try H'
    },
    'Level 4 - Bell Buddies': {
        'qubits': 2,
        'goal': lambda counts: any([counts.get(s,0) > 0 for s in ['00','11']]),
        'explain': 'Make two coins be best buddies so they always match (00 or 11). Use H then CNOT.',
        'story': "Twinny and Bubby want to match no matter how far apart they are.",
        'hint': 'H on coin 0, then CNOT 0->1'
    },
    'Level 5 - Teleportation Tunnel (Full Demo)': {
        'qubits': 3,
        'goal': lambda counts: True,
        'explain': 'Teleportation moves a coin state using entanglement and some magic messages. Press Auto-Demo to see it work.',
        'story': "A friendly wizard wants to send Spinny to a faraway place without moving him. Entangle and send the message!",
        'hint': 'Use Auto-Demo to see teleportation with corrections'
    },
    'Level 6 - Deutsch-Jozsa Detective': {
        'qubits': 1,
        'goal': lambda counts: True,
        'explain': 'Discover if a secret machine is always the same or sometimes different. Quantum magic can do it in one check!',
        'story': "Detective Qubit needs to know if the candy machine is fair. Use DJ magic.",
        'hint': 'Try Auto-Solve DJ to learn'
    },
    'Level 7 - Grover's Golden Search': {
        'qubits': 2,
        'goal': lambda counts: max(counts.values()) > 0,
        'explain': 'Find the golden chest faster using Grover magic.',
        'story': "A golden chocolate hides among dull ones — amplify its sparkle!",
        'hint': 'Try Auto-Solve Grover (2-qubit demo)'
    },
    'Level 8 - Error Detective (Bit-flip demo)': {
        'qubits': 1,
        'goal': lambda counts: True,
        'explain': 'Sometimes coins get noisy. This level shows how repetition helps detect errors.',
        'story': "Sometimes Spinny trips and flips himself. Run many shots to spot the problem.",
        'hint': 'Run multiple shots and compare counts'
    },
}

def check_puzzle_success(level_name, qubits, counts):
    if level_name not in PUZZLES:
        return False, 'No such puzzle.'
    p = PUZZLES[level_name]
    expected = p.get('qubits', qubits)
    if qubits != expected:
        return False, f'This puzzle expects {expected} coin(s).'
    ok = p['goal'](counts)
    if ok:
        return True, 'Nice! You met the puzzle goal.' 
    else:
        hint = p.get('hint', 'Try different spells.')
        return False, 'Try again. Hint: ' + hint
