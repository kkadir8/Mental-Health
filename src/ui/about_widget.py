"""
About Widget — Project information, technologies, credits.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame,
                             QHBoxLayout, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt
from ui.theme import COLORS, card_style


class AboutWidget(QWidget):
    """About page with project info and technologies used."""

    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("🧠 MindfulAI — Mental Health Assistant")
        title.setStyleSheet(f"""
            font-size: 26px; font-weight: bold;
            color: {COLORS['accent']};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("An AI-powered wellness companion that listens with empathy")
        subtitle.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Description card
        desc_card = self._make_card(
            "📖 About the Project",
            "MindfulAI is a desktop application that uses Natural Language Processing "
            "and Machine Learning to understand the emotional tone of your journal entries. "
            "Instead of showing raw clinical labels, it responds with empathy — "
            "offering supportive messages, coping strategies, and wellness resources.\n\n"
            "The model is trained on a dataset of 52,000+ mental health statements across "
            "7 categories, using TF-IDF vectorization and multiple classification algorithms."
        )
        layout.addWidget(desc_card)

        # Technologies
        tech_card = self._make_card(
            "🛠️ Technologies",
            "• Python 3.9+ — Core language\n"
            "• PyQt6 — Modern desktop GUI framework\n"
            "• scikit-learn — Machine Learning (LR, RF, SVM)\n"
            "• XGBoost — Gradient boosted classification\n"
            "• Matplotlib & Seaborn — Data visualization\n"
            "• deep-translator — Multi-language support\n"
            "• TF-IDF Vectorizer — Text feature extraction\n"
            "• JSON — Local mood journal storage"
        )
        layout.addWidget(tech_card)

        # Models
        models_card = self._make_card(
            "🤖 ML Models",
            "• Logistic Regression — Fast baseline, ~77% accuracy\n"
            "• Random Forest — Ensemble of 200 decision trees\n"
            "• XGBoost — Gradient boosting with GPU support\n"
            "• SVM (LinearSVC) — Support Vector Classification\n\n"
            "All models use stratified train/test split (80/20) and "
            "TF-IDF features (5000 dims, bigrams, min_df=2)."
        )
        layout.addWidget(models_card)

        # Features
        feat_card = self._make_card(
            "✨ Key Features",
            "• Empathetic AI Responses — No raw clinical labels shown to users\n"
            "• Multi-language Support — Write in any language, auto-translated\n"
            "• Mood Dashboard — Track your emotional journey over time\n"
            "• Guided Breathing — 3 breathing exercise techniques\n"
            "• AI Laboratory — Train & compare ML models interactively\n"
            "• Crisis Resources — Automatic safety net for high-severity states\n"
            "• Dark Theme — Modern, eye-friendly design\n"
            "• Local Storage — Your data stays on your device"
        )
        layout.addWidget(feat_card)

        # Ethics
        ethics_card = self._make_card(
            "⚖️ Ethical Note",
            "This application is NOT a substitute for professional mental health care. "
            "It provides supportive responses based on text analysis, but cannot diagnose "
            "or treat any condition. If you or someone you know is in crisis, please "
            "contact a mental health professional or crisis hotline immediately.\n\n"
            "All journal data is stored locally on your device and is never sent to "
            "any external server."
        )
        layout.addWidget(ethics_card)

        # Credits
        credits = QLabel("Made with ❤️ by kkadir8  •  GitHub: github.com/kkadir8/Mental-Health")
        credits.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_card(self, title: str, body: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(card_style())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        t = QLabel(title)
        t.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(t)

        b = QLabel(body)
        b.setWordWrap(True)
        b.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']}; line-height: 1.5;")
        layout.addWidget(b)

        return card
