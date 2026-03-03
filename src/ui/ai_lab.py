from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QComboBox, 
                             QProgressBar, QMessageBox, QTableWidget, QTableWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ui.visualization_widget import PlotCanvas
from evaluation import Evaluator


class TrainWorker(QThread):
    """Background thread for model training."""
    finished = pyqtSignal(object, object, object, object, str)
    
    def __init__(self, factory, X, y, algo_name):
        super().__init__()
        self.factory = factory
        self.X = X
        self.y = y
        self.algo_name = algo_name
        
    def run(self):
        model, X_test, y_test, y_pred = self.factory.train_model(self.X, self.y, self.algo_name)
        self.finished.emit(model, X_test, y_test, y_pred, self.algo_name)


class DataDiscoveryPanel(QWidget):
    """Panel for loading and exploring the dataset."""

    def __init__(self, pipeline):
        super().__init__()
        self.pipeline = pipeline
        self.layout = QVBoxLayout(self)
        
        top_layout = QHBoxLayout()
        self.btn_load = QPushButton("Load & Analyze Dataset")
        self.btn_load.setStyleSheet("background-color: #3498db; color: white; padding: 8px; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_data)
        top_layout.addWidget(self.btn_load)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        top_layout.addWidget(self.info_label)
        top_layout.addStretch()
        self.layout.addLayout(top_layout)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.table = QTableWidget()
        splitter.addWidget(self.table)
        self.chart = PlotCanvas(self, width=5, height=4)
        splitter.addWidget(self.chart)
        self.layout.addWidget(splitter)
        
    def load_data(self):
        try:
            df = self.pipeline.get_raw_data()
            self.info_label.setText(f"{len(df):,} records | {df['status'].nunique()} classes | Columns: {', '.join(df.columns)}")
            
            self.table.setRowCount(min(100, len(df)))
            self.table.setColumnCount(len(df.columns))
            self.table.setHorizontalHeaderLabels(df.columns)
            for i in range(min(100, len(df))):
                for j, col in enumerate(df.columns):
                    self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i][col])))
            
            counts = self.pipeline.get_class_distribution()
            self.chart.plot_class_distribution(counts)
            QMessageBox.information(self, "Success", f"Data Loaded: {len(df):,} records with {df['status'].nunique()} classes.")
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
        self.all_results = {}  # Store results for comparison
        
        layout = QVBoxLayout(self)
        
        # Controls
        header = QHBoxLayout()
        header.addWidget(QLabel("Algorithm:"))
        self.combo_algorithm = QComboBox()
        self.combo_algorithm.addItems(["Logistic Regression", "Random Forest", "XGBoost", "SVM"])
        header.addWidget(self.combo_algorithm)
        
        self.btn_train = QPushButton("Train & Bench")
        self.btn_train.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; font-weight: bold;")
        self.btn_train.clicked.connect(self.start_training)
        header.addWidget(self.btn_train)
        
        self.btn_train_all = QPushButton("Train All Models")
        self.btn_train_all.setStyleSheet("background-color: #8e44ad; color: white; padding: 8px; font-weight: bold;")
        self.btn_train_all.clicked.connect(self.train_all_models)
        header.addWidget(self.btn_train_all)
        
        self.btn_compare = QPushButton("Compare Results")
        self.btn_compare.setStyleSheet("background-color: #2980b9; color: white; padding: 8px; font-weight: bold;")
        self.btn_compare.clicked.connect(self.show_comparison)
        self.btn_compare.setEnabled(False)
        header.addWidget(self.btn_compare)
        layout.addLayout(header)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Charts
        chart_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.chart = PlotCanvas(self, width=5, height=4)
        chart_splitter.addWidget(self.chart)
        self.chart_cm = PlotCanvas(self, width=5, height=4)
        chart_splitter.addWidget(self.chart_cm)
        layout.addWidget(chart_splitter)
        
        # Log
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(200)
        layout.addWidget(self.text_log)
        
        self._train_queue = []
        
    def start_training(self):
        try:
            if self.X is None:
                self.log("Preprocessing dataset...")
                self.X, self.y, self.class_names = self.pipeline.preprocess()
                self.log(f"Features: {self.X.shape[1]}, Samples: {self.X.shape[0]}")
            
            algo = self.combo_algorithm.currentText()
            self._run_training(algo)
        except Exception as e:
            self.log(f"Error: {e}")
            self.progress.setVisible(False)
            self.btn_train.setEnabled(True)

    def train_all_models(self):
        """Train all algorithms sequentially."""
        try:
            if self.X is None:
                self.log("Preprocessing dataset...")
                self.X, self.y, self.class_names = self.pipeline.preprocess()
                self.log(f"Features: {self.X.shape[1]}, Samples: {self.X.shape[0]}")
            
            self._train_queue = ["Logistic Regression", "Random Forest", "XGBoost", "SVM"]
            self.log("=== Training All Models ===")
            self._train_next_in_queue()
        except Exception as e:
            self.log(f"Error: {e}")
    
    def _train_next_in_queue(self):
        if self._train_queue:
            algo = self._train_queue.pop(0)
            self._run_training(algo)
        else:
            self.log("=== All Models Trained ===")
            self.show_comparison()

    def _run_training(self, algo):
        self.log(f"Training {algo}...")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_train.setEnabled(False)
        self.btn_train_all.setEnabled(False)
        
        self.worker = TrainWorker(self.factory, self.X, self.y, algo)
        self.worker.finished.connect(self.on_training_finished)
        self.worker.start()

    def on_training_finished(self, model, X_test, y_test, y_pred, name):
        self.progress.setVisible(False)
        self.btn_train.setEnabled(True)
        self.btn_train_all.setEnabled(True)
        
        metrics = Evaluator.calculate_metrics(y_test, y_pred)
        self.all_results[name] = metrics
        
        self.chart.plot_metrics(metrics, name)
        
        # Show confusion matrix
        cm = Evaluator.get_confusion_matrix(y_test, y_pred)
        self.chart_cm.plot_confusion_matrix(cm, self.class_names)
        
        self.log(f"{name} | Acc: {metrics['accuracy']:.4f} | F1: {metrics['f1']:.4f} | Prec: {metrics['precision']:.4f} | Rec: {metrics['recall']:.4f}")
        
        if len(self.all_results) >= 2:
            self.btn_compare.setEnabled(True)
        
        # Notify Journal that a model is available
        self.model_ready.emit(self.class_names)
        
        # Continue queue if training all
        if self._train_queue:
            self._train_next_in_queue()

    def show_comparison(self):
        if len(self.all_results) < 2:
            QMessageBox.information(self, "Info", "Train at least 2 models to compare.")
            return
        self.chart.plot_comparison(self.all_results)
        
        # Log comparison table
        self.log("\n--- Model Comparison ---")
        self.log(f"{'Model':<25} {'Accuracy':>10} {'F1':>10} {'Precision':>10} {'Recall':>10}")
        self.log("-" * 65)
        for name, m in sorted(self.all_results.items(), key=lambda x: x[1]['f1'], reverse=True):
            self.log(f"{name:<25} {m['accuracy']:>10.4f} {m['f1']:>10.4f} {m['precision']:>10.4f} {m['recall']:>10.4f}")

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
        
        self.addTab(self.data_tab, "Data Discovery")
        self.addTab(self.bench_tab, "Model Comparison")
