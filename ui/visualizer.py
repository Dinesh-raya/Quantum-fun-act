
import matplotlib.pyplot as plt
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

def plot_counts_figure(counts):
    labels = sorted(counts.keys(), reverse=True)
    values = [counts[k] for k in labels]
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel('States (bitstrings)')
    ax.set_ylabel('Counts')
    ax.set_title('Measurement outcomes')
    return fig

def plot_bloch_plotly(statevector):
    if not PLOTLY_AVAILABLE:
        return None
    # simplified: plot a point roughly on the Bloch sphere
    x = 0; y = 0; z = 1
    import plotly.graph_objects as go, numpy as np
    u = np.linspace(0, 2*np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    fig = go.Figure(data=[go.Surface(x=xs, y=ys, z=zs, opacity=0.2, showscale=False),
                          go.Scatter3d(x=[x], y=[y], z=[z], mode='markers', marker=dict(size=6))])
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)))
    return fig
