"""
Main Window — Sidebar navigation with modern dark theme.
Connects Dashboard, Journal, AI Lab, Breathing Exercise, and About panels.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QFrame,
                             QSizePolicy, QApplication, QLineEdit, QDialog,
                             QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon

from ui.theme import COLORS, get_main_stylesheet
from ui.assistant_ui import DashboardPanel, JournalPanel
from ui.ai_lab import AILabWidget
from ui.breathing_widget import BreathingWidget
from ui.about_widget import AboutWidget
from llm_service import get_llm_service

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

        # Gemini AI status & settings
        self.llm_service = get_llm_service()

        self.llm_status = QLabel()
        self._update_llm_status()
        self.llm_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.llm_status)

        settings_btn = QPushButton("⚙️  Gemini API Key")
        settings_btn.setFixedHeight(36)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 12px;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin: 4px 12px;
                padding: 4px;
                background: transparent;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
            }}
        """)
        settings_btn.clicked.connect(self._show_api_key_dialog)
        layout.addWidget(settings_btn)

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

    def _update_llm_status(self):
        """Update LLM status indicator in sidebar."""
        if self.llm_service.is_available:
            self.llm_status.setText("🟢 Gemini AI Active")
            self.llm_status.setStyleSheet(f"color: {COLORS['success']}; font-size: 11px; padding: 4px;")
            self.status_label.setText("● AI Ready")
            self.status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px;")
        else:
            self.llm_status.setText("⚪ Gemini AI Off")
            self.llm_status.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; padding: 4px;")

    def _show_api_key_dialog(self):
        """Show dialog to configure Gemini API key."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Gemini API Key")
        dialog.setFixedSize(480, 280)
        dialog.setStyleSheet(f"background: {COLORS['bg_primary']}; color: {COLORS['text_primary']};")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        # Title
        title = QLabel("🤖 Google Gemini AI Configuration")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['accent']};")
        layout.addWidget(title)

        # Instructions
        info = QLabel(
            "Gemini Flash is free (15 req/min, 1M tokens/day).\n"
            "Get your API key from: https://aistudio.google.com/apikey"
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        info.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        info.setOpenExternalLinks(True)
        layout.addWidget(info)

        # API key input
        key_label = QLabel("API Key:")
        key_label.setStyleSheet(f"font-size: 13px; color: {COLORS['text_primary']};")
        layout.addWidget(key_label)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Paste your Gemini API key here...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.llm_service.api_key:
            self.key_input.setText(self.llm_service.api_key)
        self.key_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        layout.addWidget(self.key_input)

        # Buttons
        btn_layout = QHBoxLayout()

        remove_btn = QPushButton("Remove Key")
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px; border-radius: 6px;
                background: transparent; color: {COLORS['accent_orange']};
                border: 1px solid {COLORS['accent_orange']};
            }}
            QPushButton:hover {{ background: rgba(243,156,18,0.1); }}
        """)
        remove_btn.clicked.connect(lambda: self._remove_api_key(dialog))
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()

        save_btn = QPushButton("Save & Connect")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 20px; border-radius: 6px;
                background: {COLORS['accent']}; color: white;
                font-weight: bold; border: none;
            }}
            QPushButton:hover {{ background: #c0392b; }}
        """)
        save_btn.clicked.connect(lambda: self._save_api_key(dialog))
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        dialog.exec()

    def _save_api_key(self, dialog: QDialog):
        """Save and test the API key."""
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Error", "Please enter an API key.")
            return

        success = self.llm_service.set_api_key(key)
        if success:
            self._update_llm_status()
            QMessageBox.information(self, "Success",
                                   "✅ Gemini AI connected successfully!\n"
                                   "Journal responses will now be powered by AI.")
            dialog.accept()
        else:
            QMessageBox.warning(self, "Failed",
                                "❌ Could not connect to Gemini.\n"
                                "Please check your API key and try again.")

    def _remove_api_key(self, dialog: QDialog):
        """Remove stored API key."""
        self.llm_service.remove_api_key()
        self.key_input.clear()
        self._update_llm_status()
        QMessageBox.information(self, "Removed",
                                "API key removed. Template responses will be used.")
        dialog.accept()

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
