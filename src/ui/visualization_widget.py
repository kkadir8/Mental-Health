try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Use a compatible style
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except OSError:
    plt.style.use('ggplot')


class PlotCanvas(FigureCanvas):
    """Reusable matplotlib canvas widget for PyQt6."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)

    def plot_class_distribution(self, value_counts):
        self.axes.clear()
        colors = sns.color_palette("viridis", len(value_counts))
        bars = self.axes.bar(range(len(value_counts)), value_counts.values, color=colors)
        self.axes.set_xticks(range(len(value_counts)))
        self.axes.set_xticklabels(value_counts.index, rotation=45, ha='right')
        self.axes.set_title("Class Distribution", fontweight='bold')
        self.axes.set_xlabel("Mental Health Status")
        self.axes.set_ylabel("Count")
        # Add value labels on bars
        for bar, val in zip(bars, value_counts.values):
            self.axes.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                          f'{val:,}', ha='center', va='bottom', fontsize=8)
        self.fig.tight_layout()
        self.draw()

    def plot_metrics(self, metrics_dict, model_name):
        self.axes.clear()
        names = list(metrics_dict.keys())
        values = list(metrics_dict.values())
        colors = sns.color_palette("magma", len(names))

        bars = self.axes.bar(range(len(names)), values, color=colors)
        self.axes.set_xticks(range(len(names)))
        self.axes.set_xticklabels([n.capitalize() for n in names])
        self.axes.set_title(f"Performance Metrics: {model_name}", fontweight='bold')
        self.axes.set_ylim(0, 1.05)
        for i, v in enumerate(values):
            self.axes.text(i, v + 0.02, f"{v:.3f}", ha='center', fontweight='bold')
        self.fig.tight_layout()
        self.draw()

    def plot_confusion_matrix(self, cm, class_names):
        """Plot confusion matrix heatmap."""
        self.axes.clear()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=class_names, yticklabels=class_names,
                    ax=self.axes)
        self.axes.set_title('Confusion Matrix', fontweight='bold')
        self.axes.set_xlabel('Predicted')
        self.axes.set_ylabel('Actual')
        self.fig.tight_layout()
        self.draw()

    def plot_comparison(self, results_dict):
        """Plot comparison bar chart for multiple models."""
        self.axes.clear()
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        x = np.arange(len(metrics))
        width = 0.8 / len(results_dict)

        for i, (model_name, scores) in enumerate(results_dict.items()):
            values = [scores.get(m, 0) for m in metrics]
            self.axes.bar(x + i * width, values, width, label=model_name)

        self.axes.set_xticks(x + width * (len(results_dict) - 1) / 2)
        self.axes.set_xticklabels([m.capitalize() for m in metrics])
        self.axes.set_ylim(0, 1.05)
        self.axes.set_title('Model Comparison', fontweight='bold')
        self.axes.legend(loc='lower right', fontsize=8)
        self.fig.tight_layout()
        self.draw()
