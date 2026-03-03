"""
Redesigned Journal & Dashboard panels — The heart of the Mental Health Assistant.

Journal: Users write their thoughts, get empathetic AI responses (not clinical labels).
Dashboard: Mood trends, statistics cards, daily tips.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QListWidget, QMessageBox,
                             QFrame, QScrollArea, QSizePolicy, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from ui.visualization_widget import PlotCanvas
from ui.theme import COLORS, card_style, stat_card_style
from response_engine import ResponseEngine, MOOD_MAP

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False


# ======================================================================
# Helper: Create styled stat cards
# ======================================================================
def _stat_card(value, label, color="#00d2d3"):
    frame = QFrame()
    frame.setStyleSheet(stat_card_style())
    frame.setFixedHeight(90)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 8, 12, 8)
    layout.setSpacing(2)
    val_lbl = QLabel(str(value))
    val_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
    val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(val_lbl)
    desc_lbl = QLabel(label)
    desc_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['text_secondary']};")
    desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(desc_lbl)
    return frame, val_lbl


# ======================================================================
# DASHBOARD PANEL
# ======================================================================
class DashboardPanel(QWidget):
    def __init__(self, history):
        super().__init__()
        self.history = history
        self.response_engine = ResponseEngine()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Title
        title = QLabel("📊  Your Wellness Dashboard")
        title.setObjectName("section_title")
        main_layout.addWidget(title)

        # Daily Tip
        self.tip_label = QLabel(self.response_engine.get_daily_tip())
        self.tip_label.setObjectName("daily_tip")
        self.tip_label.setWordWrap(True)
        main_layout.addWidget(self.tip_label)

        # Stats Row
        stats_layout = QHBoxLayout()
        self.stat_total, self.stat_total_val = _stat_card("0", "Total Entries", "#74b9ff")
        self.stat_streak, self.stat_streak_val = _stat_card("0", "Day Streak 🔥", "#fdcb6e")
        self.stat_mood, self.stat_mood_val = _stat_card("—", "Most Frequent", "#a29bfe")
        self.stat_last, self.stat_last_val = _stat_card("—", "Last Mood", "#00d2d3")
        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_streak)
        stats_layout.addWidget(self.stat_mood)
        stats_layout.addWidget(self.stat_last)
        main_layout.addLayout(stats_layout)

        # Charts row
        charts_layout = QHBoxLayout()
        self.chart_mood = PlotCanvas(self, width=5, height=3)
        charts_layout.addWidget(self.chart_mood)
        self.chart_timeline = PlotCanvas(self, width=5, height=3)
        charts_layout.addWidget(self.chart_timeline)
        main_layout.addLayout(charts_layout)

        self.refresh()

    def refresh(self):
        stats = self.history.get_stats()
        total = stats['total']
        self.stat_total_val.setText(str(total))
        self.tip_label.setText(self.response_engine.get_daily_tip())

        counts = stats['mood_counts']
        if counts:
            most_freq = max(counts, key=counts.get)
            mood_info = self.response_engine.get_mood_info(most_freq)
            self.stat_mood_val.setText(f"{mood_info['emoji']} {mood_info['label']}")
        else:
            self.stat_mood_val.setText("—")

        if stats.get('last_entry'):
            last = stats['last_entry']
            mood_info = self.response_engine.get_mood_info(last.get('sentiment', 'Normal'))
            self.stat_last_val.setText(f"{mood_info['emoji']}")
        else:
            self.stat_last_val.setText("—")

        streak = self._calc_streak()
        self.stat_streak_val.setText(str(streak))

        # Mood distribution chart
        self._draw_mood_chart(counts)
        # Timeline chart
        self._draw_timeline()

    def _draw_mood_chart(self, counts):
        ax = self.chart_mood.axes
        ax.clear()
        self.chart_mood.fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#16213e')
        if counts:
            friendly = {}
            colors_list = []
            for cat, cnt in counts.items():
                info = MOOD_MAP.get(cat, {"label": cat, "color": "#74b9ff", "emoji": ""})
                friendly[f"{info.get('emoji', '')} {info['label']}"] = cnt
                colors_list.append(info.get('color', '#74b9ff'))
            keys = list(friendly.keys())
            vals = list(friendly.values())
            ax.bar(range(len(keys)), vals, color=colors_list)
            ax.set_xticks(range(len(keys)))
            ax.set_xticklabels(keys, rotation=30, ha='right', fontsize=8)
            ax.set_title("Mood Distribution", fontweight='bold', color='white', fontsize=11)
        else:
            ax.text(0.5, 0.5, "No data yet\nStart journaling!", ha='center', va='center', fontsize=12, color='#b2bec3')
            ax.set_title("Mood Distribution", color='white')
        ax.tick_params(colors='white', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#2d3436')
        self.chart_mood.fig.tight_layout()
        self.chart_mood.draw()

    def _draw_timeline(self):
        ax = self.chart_timeline.axes
        ax.clear()
        self.chart_timeline.fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#16213e')
        entries = self.history.entries
        if len(entries) >= 2:
            dates = [e.get('date', '') for e in entries[-20:]]
            severity_map = {cat: info['severity'] for cat, info in MOOD_MAP.items()}
            severities = [severity_map.get(e.get('sentiment', 'Normal'), 1) for e in entries[-20:]]
            ax.plot(range(len(dates)), severities, '-o', color='#e94560', linewidth=2, markersize=6)
            ax.set_ylim(0.5, 5.5)
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_yticklabels(["Good", "Stress", "Uneasy", "Low", "Crisis"], fontsize=8)
            step = max(1, len(dates) // 5)
            ax.set_xticks(range(0, len(dates), step))
            ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=30, fontsize=7)
            ax.set_title("Mood Timeline (last 20 entries)", fontweight='bold', color='white', fontsize=11)
            ax.invert_yaxis()
        else:
            ax.text(0.5, 0.5, "Need 2+ entries\nfor timeline", ha='center', va='center', fontsize=12, color='#b2bec3')
            ax.set_title("Mood Timeline", color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#2d3436')
        self.chart_timeline.fig.tight_layout()
        self.chart_timeline.draw()

    def _calc_streak(self):
        from datetime import datetime
        if not self.history.entries:
            return 0
        dates = sorted(set(e.get('date', '') for e in self.history.entries), reverse=True)
        if not dates:
            return 0
        streak = 1
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            if dates[0] != today:
                return 0
            for i in range(1, len(dates)):
                prev = datetime.strptime(dates[i - 1], "%Y-%m-%d")
                curr = datetime.strptime(dates[i], "%Y-%m-%d")
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    break
        except Exception:
            pass
        return streak


# ======================================================================
# JOURNAL PANEL — Empathetic AI response instead of raw labels
# ======================================================================
class JournalPanel(QWidget):
    def __init__(self, history, factory, pipeline):
        super().__init__()
        self.history = history
        self.factory = factory
        self.pipeline = pipeline
        self.class_names = None
        self.dashboard_ref = None
        self.response_engine = ResponseEngine()

        if HAS_TRANSLATOR:
            self.translator = GoogleTranslator(source='auto', target='en')
        else:
            self.translator = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        # Title
        title = QLabel("📝  My Journal — Talk to your AI wellness companion")
        title.setObjectName("section_title")
        main_layout.addWidget(title)

        # Input area
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_layout = QVBoxLayout(input_frame)
        prompt_label = QLabel("How are you feeling today? Write in any language...")
        prompt_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        input_layout.addWidget(prompt_label)
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Share your thoughts here... I'm listening. 💙")
        self.input_text.setFixedHeight(100)
        input_layout.addWidget(self.input_text)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💬  Share with Assistant")
        self.btn_save.setObjectName("btn_green")
        self.btn_save.clicked.connect(self.save_entry)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()
        input_layout.addLayout(btn_layout)
        main_layout.addWidget(input_frame)

        # Scrollable AI Response Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_inner = QVBoxLayout(scroll_content)

        self.response_frame = QFrame()
        self.response_frame.setObjectName("response_card")
        self.response_frame.setVisible(False)
        self.response_layout = QVBoxLayout(self.response_frame)
        self.response_layout.setSpacing(10)

        # Mood indicator
        self.mood_header = QLabel("")
        self.mood_header.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.response_layout.addWidget(self.mood_header)

        # Acknowledgment
        self.ack_label = QLabel("")
        self.ack_label.setWordWrap(True)
        self.ack_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_primary']}; line-height: 150%;")
        self.response_layout.addWidget(self.ack_label)

        # Supportive message
        self.support_label = QLabel("")
        self.support_label.setWordWrap(True)
        self.support_label.setStyleSheet(
            f"font-size: 13px; color: {COLORS['text_secondary']}; "
            f"padding: 10px; background: rgba(0,210,211,0.08); border-radius: 8px; "
            f"border-left: 3px solid {COLORS['accent_green']};")
        self.response_layout.addWidget(self.support_label)

        # Professional help (conditional)
        self.prof_label = QLabel("")
        self.prof_label.setWordWrap(True)
        self.prof_label.setStyleSheet(f"font-size: 12px; color: {COLORS['accent_orange']}; padding: 8px;")
        self.prof_label.setVisible(False)
        self.response_layout.addWidget(self.prof_label)

        # Crisis resources (conditional)
        self.crisis_frame = QFrame()
        self.crisis_frame.setObjectName("crisis_card")
        self.crisis_frame.setVisible(False)
        crisis_layout = QVBoxLayout(self.crisis_frame)
        self.crisis_label = QLabel("")
        self.crisis_label.setWordWrap(True)
        self.crisis_label.setStyleSheet("font-size: 12px; color: #e74c3c;")
        crisis_layout.addWidget(self.crisis_label)
        self.response_layout.addWidget(self.crisis_frame)

        # Follow-up prompt
        self.followup_label = QLabel("")
        self.followup_label.setWordWrap(True)
        self.followup_label.setStyleSheet(f"font-size: 13px; font-style: italic; color: {COLORS['accent_purple']};")
        self.response_layout.addWidget(self.followup_label)

        scroll_inner.addWidget(self.response_frame)

        # History section inside scroll
        history_header = QHBoxLayout()
        hist_title = QLabel("📋 Recent Journal Entries")
        hist_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['text_secondary']};")
        history_header.addWidget(hist_title)
        history_header.addStretch()
        self.btn_clear = QPushButton("🗑 Clear")
        self.btn_clear.setObjectName("btn_danger")
        self.btn_clear.setFixedHeight(28)
        self.btn_clear.setFixedWidth(90)
        self.btn_clear.clicked.connect(self.clear_history)
        history_header.addWidget(self.btn_clear)
        scroll_inner.addLayout(history_header)

        self.history_list = QListWidget()
        self.history_list.setMinimumHeight(120)
        scroll_inner.addWidget(self.history_list)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.refresh_list()

    def set_class_names(self, names):
        self.class_names = names

    def clear_history(self):
        confirm = QMessageBox.question(
            self, "Confirm",
            "Are you sure you want to delete all journal history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.history.clear_history()
            self.refresh_list()
            if self.dashboard_ref:
                self.dashboard_ref.refresh()

    def save_entry(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            return

        # Translation
        try:
            if self.translator:
                translated_text = self.translator.translate(text)
            else:
                translated_text = text
        except Exception:
            translated_text = text

        # Prediction
        if not self.factory.current_model:
            QMessageBox.warning(self, "AI Not Ready",
                                "Please go to 'AI Laboratory' and train a model first!")
            return

        sentiment = "Normal"
        confidence = 0.0
        try:
            clean_text = translated_text.lower()
            vec = self.pipeline.vectorizer.transform([clean_text])
            if self.class_names is not None:
                pred_idx = self.factory.predict(vec)[0]
                sentiment = self.class_names[pred_idx]
            else:
                sentiment = str(self.factory.predict(vec)[0])
            probs = self.factory.predict_proba(vec)
            if probs is not None:
                confidence = float(max(probs[0]))
        except Exception as e:
            print(f"Prediction error: {e}")

        # Generate empathetic response
        response = self.response_engine.generate_response(sentiment, confidence)
        self._show_response(response)

        # Save to history
        self.history.add_entry(text, sentiment, confidence)
        self.input_text.clear()
        self.refresh_list()
        if self.dashboard_ref:
            self.dashboard_ref.refresh()

    def _show_response(self, response):
        """Display the AI assistant's empathetic response."""
        self.response_frame.setVisible(True)
        self.mood_header.setText(f"{response.mood_emoji}  {response.mood_label}")
        self.mood_header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {response.mood_color};")
        self.ack_label.setText(response.acknowledgment)
        self.support_label.setText(f"💡 {response.supportive_message}")

        if response.professional_help:
            self.prof_label.setText(response.professional_help)
            self.prof_label.setVisible(True)
        else:
            self.prof_label.setVisible(False)

        if response.crisis_resources:
            self.crisis_frame.setVisible(True)
            self.crisis_label.setText(response.crisis_resources)
        else:
            self.crisis_frame.setVisible(False)

        self.followup_label.setText(f"💭 Journal prompt: {response.followup_prompt}")

    def refresh_list(self):
        self.history_list.clear()
        for entry in reversed(self.history.entries):
            mood_info = MOOD_MAP.get(entry.get('sentiment', 'Normal'),
                                     {"label": "Unknown", "emoji": "❓", "color": "#7f8c8d"})
            conf = entry.get('confidence', 0)
            item_text = (f"{mood_info['emoji']}  {entry.get('date', '')}  —  "
                         f"{mood_info['label']}  ({conf:.0%})  |  "
                         f"\"{entry.get('text', '')[:60]}\"")
            self.history_list.addItem(QListWidgetItem(item_text))
