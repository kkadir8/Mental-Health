from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QListWidget, QMessageBox)
from PyQt6.QtCore import Qt
from ui.visualization_widget import PlotCanvas
import matplotlib.pyplot as plt
import seaborn as sns
from deep_translator import GoogleTranslator

class DashboardPanel(QWidget):
    def __init__(self, history):
        super().__init__()
        self.history = history
        self.layout = QVBoxLayout(self)
        
        # Stats Row
        self.stats_label = QLabel("Loading stats...")
        self.stats_label.setStyleSheet("font-size: 16px; padding: 10px; background: #ecf0f1; color: #2c3e50; border-radius: 5px;")
        self.layout.addWidget(self.stats_label)
        
        # Trend Chart
        self.chart = PlotCanvas(self, width=5, height=4)
        self.layout.addWidget(self.chart)
        
        self.refresh()

    def refresh(self):
        stats = self.history.get_stats()
        
        # Update Label
        msg = f"Total Entries: {stats['total']}\n"
        if stats.get('last_entry'):
            msg += f"Last Mood: {stats['last_entry']['sentiment']} ({stats['last_entry']['date']})"
        self.stats_label.setText(msg)
        
        # Update Chart (Timeline of Anxiety/Normal etc)
        # Always clear axes first
        self.chart.axes.clear()
        
        counts = stats['mood_counts']
        if counts:
            sns.barplot(x=list(counts.keys()), y=list(counts.values()), ax=self.chart.axes, palette="rocket")
            self.chart.axes.set_title("My Mood Summary")
        else:
            self.chart.axes.text(0.5, 0.5, "No Data Available", ha='center', va='center')
            self.chart.axes.set_title("My Mood Summary (Empty)")
            
        self.chart.draw()

class JournalPanel(QWidget):
    def __init__(self, history, factory, pipeline):
        super().__init__()
        self.history = history
        self.factory = factory
        self.pipeline = pipeline
        self.class_names = None
        self.dashboard_ref = None # To refresh dashboard
        self.translator = GoogleTranslator(source='auto', target='en')
        
        self.layout = QVBoxLayout(self)
        
        self.layout.addWidget(QLabel("How are you feeling today? (Write your thoughts in Turkish or English)"))
        self.input_text = QTextEdit()
        self.layout.addWidget(self.input_text)
        
        self.btn_save = QPushButton("Analyze & Save to Journal")
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_entry)
        self.layout.addWidget(self.btn_save)
        
        # History Header with Clear Button
        history_sys_layout = QHBoxLayout()
        history_sys_layout.addWidget(QLabel("Recent History:"))
        
        self.btn_clear = QPushButton("Clear History")
        self.btn_clear.setFixedSize(100, 30)
        self.btn_clear.setStyleSheet("background-color: #c0392b; color: white; border-radius: 5px;")
        self.btn_clear.clicked.connect(self.clear_history)
        history_sys_layout.addWidget(self.btn_clear)
        history_sys_layout.addStretch()
        
        self.layout.addLayout(history_sys_layout)
        self.history_list = QListWidget()
        self.layout.addWidget(self.history_list)
        
        self.refresh_list()

    def clear_history(self):
        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to delete all journal history?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.history.clear_history()
            self.refresh_list()
            if self.dashboard_ref:
                self.dashboard_ref.refresh()

    def set_class_names(self, names):
        self.class_names = names

    def save_entry(self):
        text = self.input_text.toPlainText()
        if not text:
            return
            
        # Translation
        try:
            translated_text = self.translator.translate(text)
            print(f"Original: {text} -> Translated: {translated_text}") 
        except Exception as e:
            print(f"Translation failed: {e}")
            translated_text = text # Fallback

        # Prediction
        sentiment = "Unknown"
        confidence = 0.0
        
        if self.factory.current_model:
            try:
                clean_text = translated_text.lower()
                vec = self.pipeline.vectorizer.transform([clean_text])
                
                # Predict
                if self.class_names is not None:
                    pred_idx = self.factory.predict(vec)[0]
                    sentiment = self.class_names[pred_idx]
                else:
                    sentiment = str(self.factory.predict(vec)[0])
                    
                # Confidence
                probs = self.factory.predict_proba(vec)
                if probs is not None:
                    confidence = max(probs[0])
            except Exception as e:
                print(f"Pred error: {e}")
        else:
            QMessageBox.warning(self, "AI Not Ready", "Please go to 'AI Lab' and train a model first!")
            return

        # Save
        self.history.add_entry(text, sentiment, confidence)
        self.input_text.clear()
        self.refresh_list()
        
        if self.dashboard_ref:
            self.dashboard_ref.refresh()
            
        QMessageBox.information(self, "Saved", f"Entry saved!\nAnalysis: {sentiment}\n(Translated: {translated_text})")

    def refresh_list(self):
        self.history_list.clear()
        for i, entry in enumerate(reversed(self.history.entries)):
            self.history_list.addItem(f"{entry['date']} - {entry['sentiment']}: {entry['text'][:50]}...")
