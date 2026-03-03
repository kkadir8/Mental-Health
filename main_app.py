"""
MindfulAI — Mental Health Assistant
Entry point: apply dark theme, create application window.
"""

import sys
import os

# Add src/ to path so imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from ui.theme import get_main_stylesheet
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Apply dark theme
    app.setStyleSheet(get_main_stylesheet())

    # Default font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
