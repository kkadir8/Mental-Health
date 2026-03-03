"""
Visualization widgets — Matplotlib canvas for PyQt6.
Updated for dark theme and additional chart types.
"""

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Dark theme for matplotlib
DARK_BG = '#1a1a2e'
DARK_FG = '#16213e'
TEXT_COLOR = '#ffffff'
GRID_COLOR = '#2d3436'


class PlotCanvas(FigureCanvas):
    """Reusable matplotlib canvas widget for PyQt6 with dark theme."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor(DARK_BG)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor(DARK_FG)
        self._apply_dark_theme()
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)

    def _apply_dark_theme(self):
        """Apply dark theme to axes."""
        self.axes.tick_params(colors=TEXT_COLOR, labelsize=9)
        self.axes.xaxis.label.set_color(TEXT_COLOR)
        self.axes.yaxis.label.set_color(TEXT_COLOR)
        self.axes.title.set_color(TEXT_COLOR)
        for spine in self.axes.spines.values():
            spine.set_color(GRID_COLOR)

    def _reset(self):
        """Clear and reset to dark theme."""
        self.axes.clear()
        self.fig.patch.set_facecolor(DARK_BG)
        self.axes.set_facecolor(DARK_FG)
        self._apply_dark_theme()

    def plot_class_distribution(self, value_counts):
        self._reset()
        colors = sns.color_palette("viridis", len(value_counts))
        bars = self.axes.bar(range(len(value_counts)), value_counts.values, color=colors)
        self.axes.set_xticks(range(len(value_counts)))
        self.axes.set_xticklabels(value_counts.index, rotation=45, ha='right', fontsize=8, color=TEXT_COLOR)
        self.axes.set_title("Class Distribution", fontweight='bold', color=TEXT_COLOR)
        self.axes.set_xlabel("Mental Health Status", color=TEXT_COLOR)
        self.axes.set_ylabel("Count", color=TEXT_COLOR)
        for bar, val in zip(bars, value_counts.values):
            self.axes.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                           f'{val:,}', ha='center', va='bottom', fontsize=8, color=TEXT_COLOR)
        self.fig.tight_layout()
        self.draw()

    def plot_metrics(self, metrics_dict, model_name):
        self._reset()
        display_keys = ['accuracy', 'precision', 'recall', 'f1']
        names = [k for k in display_keys if k in metrics_dict]
        values = [metrics_dict[k] for k in names]
        colors = sns.color_palette("magma", len(names))

        bars = self.axes.bar(range(len(names)), values, color=colors)
        self.axes.set_xticks(range(len(names)))
        self.axes.set_xticklabels([n.capitalize() for n in names], color=TEXT_COLOR)
        self.axes.set_title(f"Performance: {model_name}", fontweight='bold', color=TEXT_COLOR)
        self.axes.set_ylim(0, 1.05)
        for i, v in enumerate(values):
            self.axes.text(i, v + 0.02, f"{v:.3f}", ha='center', fontweight='bold',
                           color=TEXT_COLOR, fontsize=10)
        self.fig.tight_layout()
        self.draw()

    def plot_confusion_matrix(self, cm, class_names):
        """Plot confusion matrix heatmap."""
        self._reset()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=class_names, yticklabels=class_names,
                    ax=self.axes, cbar_kws={'shrink': 0.8},
                    annot_kws={'fontsize': 8, 'color': TEXT_COLOR})
        self.axes.set_title('Confusion Matrix', fontweight='bold', color=TEXT_COLOR)
        self.axes.set_xlabel('Predicted', color=TEXT_COLOR)
        self.axes.set_ylabel('Actual', color=TEXT_COLOR)
        self.axes.tick_params(labelsize=7, colors=TEXT_COLOR)
        self.fig.tight_layout()
        self.draw()

    def plot_comparison(self, results_dict):
        """Plot comparison bar chart for multiple models."""
        self._reset()
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        x = np.arange(len(metrics))
        n_models = len(results_dict)
        width = 0.8 / max(n_models, 1)

        palette = sns.color_palette("Set2", n_models)
        for i, (model_name, scores) in enumerate(results_dict.items()):
            values = [scores.get(m, 0) for m in metrics]
            self.axes.bar(x + i * width, values, width, label=model_name, color=palette[i])

        self.axes.set_xticks(x + width * (n_models - 1) / 2)
        self.axes.set_xticklabels([m.capitalize() for m in metrics], color=TEXT_COLOR)
        self.axes.set_ylim(0, 1.05)
        self.axes.set_title('Model Comparison', fontweight='bold', color=TEXT_COLOR)
        self.axes.legend(loc='lower right', fontsize=8, facecolor=DARK_FG,
                         edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
        self.fig.tight_layout()
        self.draw()
