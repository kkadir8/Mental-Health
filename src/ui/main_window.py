"""
Main Window — Sidebar navigation with modern dark theme.
Connects Dashboard, Journal, AI Lab, Breathing Exercise, and About panels.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QFrame,
                             QSizePolicy, QApplication)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon

from ui.theme import COLORS, get_main_stylesheet
from ui.assistant_ui import DashboardPanel, JournalPanel
from ui.ai_lab import AILabWidget
from ui.breathing_widget import BreathingWidget
from ui.about_widget import AboutWidget

from data_pipeline import DataPipeline
from model_factory import ModelFactory
from user_history import UserHistory


class SidebarButton(QPushButton):
    """Custom sidebar navigation button."""

    def __init__(self, emoji, text, parent=None):
        super().__init__(parent)
        self.emoji = emoji
        self.label_text = text
        self.setText(f"  {emoji}   {text}")
        self.setFixedHeight(48)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(self._normal_style())

    def _normal_style(self):
        return f"""
            QPushButton {{
                text-align: left;
                padding-left: 16px;
                font-size: 14px;
                font-weight: 500;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 10px;
                margin: 2px 8px;
                background: transparent;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:checked {{
                background: {COLORS['accent']};
                color: #ffffff;
                font-weight: 600;
            }}
        """


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 MindfulAI — Mental Health Assistant")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)

        # --- Core components ---
        self.pipeline = DataPipeline()
        self.factory = ModelFactory()
        self.history = UserHistory()

        # --- Central widget ---
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        # --- Content area ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        header = self._build_header()
        content_layout.addWidget(header)

        # Stacked pages
        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages)

        root_layout.addWidget(content_area, stretch=1)

        # --- Create pages ---
        self.dashboard_panel = DashboardPanel(self.history)
        self.journal_panel = JournalPanel(self.history, self.factory, self.pipeline)
        self.journal_panel.dashboard_ref = self.dashboard_panel
        self.ai_lab = AILabWidget(self.pipeline, self.factory)
        self.breathing = BreathingWidget()
        self.about = AboutWidget()

        self.pages.addWidget(self.dashboard_panel)  # 0
        self.pages.addWidget(self.journal_panel)      # 1
        self.pages.addWidget(self.ai_lab)              # 2
        self.pages.addWidget(self.breathing)           # 3
        self.pages.addWidget(self.about)               # 4

        # Default to dashboard
        self.nav_buttons[0].setChecked(True)
        self.pages.setCurrentIndex(0)

    def _build_sidebar(self) -> QWidget:
        """Build the sidebar with navigation buttons."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            #sidebar {{
                background-color: {COLORS['bg_primary']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Logo area
        logo_frame = QFrame()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(16, 20, 16, 20)

        logo_text = QLabel("🧠 MindfulAI")
        logo_text.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['accent']};
        """)
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_text)

        tagline = QLabel("Your Wellness Companion")
        tagline.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
        """)
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(tagline)

        layout.addWidget(logo_frame)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard"),
            ("📝", "Journal"),
            ("🔬", "AI Laboratory"),
            ("🌬️", "Breathing"),
            ("ℹ️", "About"),
        ]
        self.nav_buttons: list[SidebarButton] = []
        for emoji, text in nav_items:
            btn = SidebarButton(emoji, text)
            btn.clicked.connect(self._make_nav_handler(len(self.nav_buttons)))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # Version label at bottom
        version = QLabel("v2.0.0")
        version.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        layout.addSpacing(12)

        return sidebar

    def _build_header(self) -> QWidget:
        """Build the top header bar."""
        header = QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            #header_bar {{
                background-color: {COLORS['bg_primary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)

        self.page_title = QLabel("📊  Dashboard")
        self.page_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(self.page_title)
        layout.addStretch()

        # Status indicator
        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px;")
        layout.addWidget(self.status_label)

        return header

    def _make_nav_handler(self, index):
        """Create click handler for nav button at given index."""
        titles = [
            "📊  Dashboard",
            "📝  Journal",
            "🔬  AI Laboratory",
            "🌬️  Breathing Exercise",
            "ℹ️  About",
        ]

        def handler():
            # Uncheck all other buttons
            for i, btn in enumerate(self.nav_buttons):
                btn.setChecked(i == index)

            self.pages.setCurrentIndex(index)
            self.page_title.setText(titles[index])

            # Refresh dashboard when switching to it
            if index == 0:
                self.dashboard_panel.refresh()

        return handler
