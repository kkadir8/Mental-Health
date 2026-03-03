from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QApplication)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
import sys
import os

# Modules
from data_pipeline import DataPipeline
from model_factory import ModelFactory
from user_history import UserHistory
from ui.assistant_ui import DashboardPanel, JournalPanel
from ui.ai_lab import AILabWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mental Health Assistant (with AI Engine)")
        self.resize(1200, 800)
        
        # Set Window Icon
        logo_path = os.path.join(os.getcwd(), "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        # Backend
        self.pipeline = DataPipeline()
        self.factory = ModelFactory()
        self.history = UserHistory()
        
        # UI Components
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header Area
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo in Header (Optional)
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            # Add some padding/margin if needed
            logo_label.setStyleSheet("padding: 10px; background-color: #f7f9f9;")
            header_layout.addWidget(logo_label)

        # Text Area (Title + Author)
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        header = QLabel("Mental Health Assistant & AI Lab")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; background-color: transparent;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_layout.addWidget(header)
        
        # Author Credit
        author_label = QLabel("Created by Kadir Gedik")
        author_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-style: italic; background-color: transparent; margin-bottom: 5px;")
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        text_layout.addWidget(author_label)
        
        header_layout.addLayout(text_layout)
        
        # Wrap header in a container to ensure background covers full width
        header_container = QWidget()
        header_container.setStyleSheet("background-color: #f7f9f9;")
        header_container.setLayout(header_layout)
        
        main_layout.addWidget(header_container)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #bdc3c7; }
            QTabBar::tab { height: 40px; width: 150px; font-size: 14px; }
        """)
        
        # 1. Dashboard
        self.dashboard = DashboardPanel(self.history)
        self.tabs.addTab(self.dashboard, "📊 Dashboard")
        
        # 2. Journal
        self.journal = JournalPanel(self.history, self.factory, self.pipeline)
        self.journal.dashboard_ref = self.dashboard # Link for auto-refresh
        self.tabs.addTab(self.journal, "📝 My Journal")
        
        # 3. AI Lab (Admin)
        self.ai_lab = AILabWidget(self.pipeline, self.factory)
        # Connect AI Lab training signal to Journal
        self.ai_lab.bench_tab.model_ready.connect(self.journal.set_class_names)
        self.tabs.addTab(self.ai_lab, "🤖 AI Laboratory")
        
        main_layout.addWidget(self.tabs)
        
        self.statusBar().showMessage("System Ready. Please train a model in AI Lab first.")
