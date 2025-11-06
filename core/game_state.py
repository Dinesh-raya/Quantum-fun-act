
def init_state(session):
    if 'xp' not in session: session['xp']=0
    if 'badges' not in session: session['badges']=[]
    if 'campaign_progress' not in session: session['campaign_progress']=0

def award_xp(session, amount):
    session['xp'] = session.get('xp',0) + amount

def award_badge(session, name):
    if name not in session.get('badges', []):
        session.setdefault('badges', []).append(name)
