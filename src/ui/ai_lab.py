"""
AI Laboratory — Data Discovery, Model Training, Benchmarking & Comparison.
Now includes: training time display, per-class metrics, confusion matrix,
hyperparameter info, and model comparison charts.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QPushButton, QTextEdit, QComboBox,
                             QProgressBar, QMessageBox, QTableWidget,
                             QTableWidgetItem, QSplitter, QFrame, QSpinBox,
                             QDoubleSpinBox, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QElapsedTimer
from ui.visualization_widget import PlotCanvas
from ui.theme import COLORS
from evaluation import Evaluator
import time


class TrainWorker(QThread):
    """Background thread for model training with elapsed time tracking."""
    finished = pyqtSignal(object, object, object, object, str, float)  # added elapsed_sec

    def __init__(self, factory, X, y, algo_name):
        super().__init__()
        self.factory = factory
        self.X = X
        self.y = y
        self.algo_name = algo_name

    def run(self):
        start = time.time()
        model, X_test, y_test, y_pred = self.factory.train_model(
            self.X, self.y, self.algo_name
        )
        elapsed = time.time() - start
        self.finished.emit(model, X_test, y_test, y_pred, self.algo_name, elapsed)


class DataDiscoveryPanel(QWidget):
    """Panel for loading and exploring the dataset."""

    def __init__(self, pipeline):
        super().__init__()
        self.pipeline = pipeline
        layout = QVBoxLayout(self)

        # Controls
        top_layout = QHBoxLayout()
        self.btn_load = QPushButton("📂  Load & Analyze Dataset")
        self.btn_load.setObjectName("btn_blue")
        self.btn_load.clicked.connect(self.load_data)
        top_layout.addWidget(self.btn_load)
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; padding: 5px;")
        top_layout.addWidget(self.info_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Data table + chart
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.table = QTableWidget()
        splitter.addWidget(self.table)
        self.chart = PlotCanvas(self, width=5, height=4)
        splitter.addWidget(self.chart)
        layout.addWidget(splitter)

        # Text statistics frame
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("card")
        self.stats_frame.setVisible(False)
        stats_layout = QVBoxLayout(self.stats_frame)
        self.stats_text = QLabel("")
        self.stats_text.setWordWrap(True)
        self.stats_text.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        stats_layout.addWidget(self.stats_text)
        layout.addWidget(self.stats_frame)

    def load_data(self):
        try:
            df = self.pipeline.get_raw_data()
            n_rows = len(df)
            n_classes = df['status'].nunique()
            self.info_label.setText(f"✅ {n_rows:,} records | {n_classes} classes")

            # Table
            show_n = min(100, n_rows)
            self.table.setRowCount(show_n)
            self.table.setColumnCount(len(df.columns))
            self.table.setHorizontalHeaderLabels(list(df.columns))
            for i in range(show_n):
                for j, col in enumerate(df.columns):
                    self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i][col])))

            # Chart
            counts = self.pipeline.get_class_distribution()
            self.chart.plot_class_distribution(counts)

            # Text statistics
            avg_len = df['statement'].str.len().mean()
            max_len = df['statement'].str.len().max()
            min_len = df['statement'].str.len().min()
            self.stats_text.setText(
                f"📊 Text Statistics — Avg length: {avg_len:.0f} chars | "
                f"Max: {max_len} | Min: {min_len} | "
                f"Classes: {', '.join(df['status'].unique())}"
            )
            self.stats_frame.setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ModelBenchmarkingPanel(QWidget):
    """Panel for training, benchmarking and comparing models."""
    model_ready = pyqtSignal(object)

    def __init__(self, pipeline, factory):
        super().__init__()
        self.pipeline = pipeline
        self.factory = factory
        self.X = None
        self.y = None
        self.class_names = None
        self.all_results = {}
        self._train_queue = []

        layout = QVBoxLayout(self)

        # Controls
        header = QHBoxLayout()
        header.addWidget(QLabel("Algorithm:"))
        self.combo_algorithm = QComboBox()
        self.combo_algorithm.addItems([
            "Logistic Regression", "Random Forest", "XGBoost", "SVM"
        ])
        header.addWidget(self.combo_algorithm)

        self.btn_train = QPushButton("⚡ Train & Bench")
        self.btn_train.setObjectName("btn_green")
        self.btn_train.clicked.connect(self.start_training)
        header.addWidget(self.btn_train)

        self.btn_train_all = QPushButton("🚀 Train All Models")
        self.btn_train_all.setObjectName("btn_purple")
        self.btn_train_all.clicked.connect(self.train_all_models)
        header.addWidget(self.btn_train_all)

        self.btn_compare = QPushButton("📊 Compare Results")
        self.btn_compare.setObjectName("btn_blue")
        self.btn_compare.clicked.connect(self.show_comparison)
        self.btn_compare.setEnabled(False)
        header.addWidget(self.btn_compare)
        layout.addLayout(header)

        # Progress bar with time label
        prog_layout = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        prog_layout.addWidget(self.progress)
        self.time_label = QLabel("")
        self.time_label.setStyleSheet(f"color: {COLORS['accent_green']}; font-weight: bold; font-size: 12px;")
        prog_layout.addWidget(self.time_label)
        layout.addLayout(prog_layout)

        # Charts — metrics + confusion matrix
        chart_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.chart = PlotCanvas(self, width=5, height=4)
        chart_splitter.addWidget(self.chart)
        self.chart_cm = PlotCanvas(self, width=5, height=4)
        chart_splitter.addWidget(self.chart_cm)
        layout.addWidget(chart_splitter)

        # Log
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(180)
        self.text_log.setStyleSheet(f"font-family: 'Consolas', 'Monaco', monospace; font-size: 12px;")
        layout.addWidget(self.text_log)

    def start_training(self):
        try:
            if self.X is None:
                self.log("⏳ Preprocessing dataset...")
                self.X, self.y, self.class_names = self.pipeline.preprocess()
                self.log(f"✅ Features: {self.X.shape[1]:,} | Samples: {self.X.shape[0]:,}")
            algo = self.combo_algorithm.currentText()
            self._run_training(algo)
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.progress.setVisible(False)
            self.btn_train.setEnabled(True)

    def train_all_models(self):
        try:
            if self.X is None:
                self.log("⏳ Preprocessing dataset...")
                self.X, self.y, self.class_names = self.pipeline.preprocess()
                self.log(f"✅ Features: {self.X.shape[1]:,} | Samples: {self.X.shape[0]:,}")
            self._train_queue = ["Logistic Regression", "Random Forest", "XGBoost", "SVM"]
            self.log("\n" + "=" * 50)
            self.log("🚀 Training All Models...")
            self.log("=" * 50)
            self._train_next_in_queue()
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def _train_next_in_queue(self):
        if self._train_queue:
            algo = self._train_queue.pop(0)
            self._run_training(algo)
        else:
            self.log("\n✅ All Models Trained!")
            self.show_comparison()

    def _run_training(self, algo):
        self.log(f"\n🔄 Training {algo}...")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.time_label.setText("Training...")
        self.btn_train.setEnabled(False)
        self.btn_train_all.setEnabled(False)

        self.worker = TrainWorker(self.factory, self.X, self.y, algo)
        self.worker.finished.connect(self.on_training_finished)
        self.worker.start()

    def on_training_finished(self, model, X_test, y_test, y_pred, name, elapsed):
        self.progress.setVisible(False)
        self.btn_train.setEnabled(True)
        self.btn_train_all.setEnabled(True)
        self.time_label.setText(f"⏱ {name}: {elapsed:.1f}s")

        metrics = Evaluator.calculate_metrics(y_test, y_pred)
        metrics['training_time'] = elapsed
        self.all_results[name] = metrics

        self.chart.plot_metrics(metrics, name)

        # Confusion matrix
        cm = Evaluator.get_confusion_matrix(y_test, y_pred)
        self.chart_cm.plot_confusion_matrix(cm, self.class_names)

        # Classification report
        report = Evaluator.get_classification_report(y_test, y_pred, class_names=list(self.class_names))

        self.log(f"✅ {name} — Acc: {metrics['accuracy']:.4f} | F1: {metrics['f1']:.4f} | "
                 f"Prec: {metrics['precision']:.4f} | Rec: {metrics['recall']:.4f} | ⏱ {elapsed:.1f}s")
        self.log(f"\n{report}")

        if len(self.all_results) >= 2:
            self.btn_compare.setEnabled(True)

        self.model_ready.emit(self.class_names)

        if self._train_queue:
            self._train_next_in_queue()

    def show_comparison(self):
        if len(self.all_results) < 2:
            QMessageBox.information(self, "Info", "Train at least 2 models to compare.")
            return
        self.chart.plot_comparison(self.all_results)

        self.log("\n" + "=" * 70)
        self.log(f"{'Model':<25} {'Accuracy':>10} {'F1':>10} {'Precision':>10} {'Recall':>10} {'Time(s)':>10}")
        self.log("-" * 70)
        for name, m in sorted(self.all_results.items(), key=lambda x: x[1]['f1'], reverse=True):
            t = m.get('training_time', 0)
            self.log(f"{name:<25} {m['accuracy']:>10.4f} {m['f1']:>10.4f} "
                     f"{m['precision']:>10.4f} {m['recall']:>10.4f} {t:>10.1f}")
        self.log("=" * 70)

    def log(self, msg):
        self.text_log.append(msg)


class AILabWidget(QTabWidget):
    """Main AI Laboratory tab widget."""

    def __init__(self, pipeline, factory):
        super().__init__()
        self.pipeline = pipeline
        self.factory = factory

        self.data_tab = DataDiscoveryPanel(pipeline)
        self.bench_tab = ModelBenchmarkingPanel(pipeline, factory)

        self.addTab(self.data_tab, "📊 Data Discovery")
        self.addTab(self.bench_tab, "🧪 Model Comparison")
