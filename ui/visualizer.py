
import matplotlib.pyplot as plt
def plot_counts_figure(counts):
    labels = sorted(counts.keys(), reverse=True)
    values = [counts[k] for k in labels]
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel('States (bitstrings)')
    ax.set_ylabel('Counts')
    ax.set_title('Measurement outcomes')
    return fig
