"""
Breathing Exercise Widget — Guided animated breathing exercise.
Uses QTimer-based animation for inhale/hold/exhale visualization.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QFont


TECHNIQUES = {
    "4-7-8 Relaxing": {"inhale": 4, "hold": 7, "exhale": 8, "desc": "Best for anxiety & sleep"},
    "Box Breathing":   {"inhale": 4, "hold": 4, "exhale": 4, "desc": "Used by Navy SEALs for focus"},
    "Calm Breath":     {"inhale": 4, "hold": 2, "exhale": 6, "desc": "Quick daily calm-down"},
}


class BreathCircle(QWidget):
    """Animated circle that grows/shrinks with breathing phases."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 40
        self._phase_text = "Ready"
        self._phase_color = QColor("#00d2d3")
        self.setMinimumSize(250, 250)

    def get_radius(self):
        return self._radius

    def set_radius(self, value):
        self._radius = value
        self.update()

    radius = pyqtProperty(int, get_radius, set_radius)

    def set_phase(self, text, color_hex):
        self._phase_text = text
        self._phase_color = QColor(color_hex)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() // 2
        cy = self.height() // 2
        r = self._radius

        # Glow gradient
        gradient = QRadialGradient(cx, cy, r + 20)
        gradient.setColorAt(0, QColor(self._phase_color.red(), self._phase_color.green(), self._phase_color.blue(), 120))
        gradient.setColorAt(0.7, QColor(self._phase_color.red(), self._phase_color.green(), self._phase_color.blue(), 60))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - r - 20, cy - r - 20, (r + 20) * 2, (r + 20) * 2)

        # Main circle
        gradient2 = QRadialGradient(cx, cy, r)
        gradient2.setColorAt(0, self._phase_color)
        c2 = QColor(self._phase_color)
        c2.setAlpha(180)
        gradient2.setColorAt(1, c2)
        painter.setBrush(gradient2)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Phase text
        painter.setPen(QColor("white"))
        font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._phase_text)

        painter.end()


class BreathingWidget(QWidget):
    """Complete breathing exercise panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.current_phase = 0  # 0=inhale, 1=hold, 2=exhale
        self.phase_timer = QTimer()
        self.phase_timer.timeout.connect(self._next_phase)
        self.cycles_done = 0
        self.total_cycles = 3

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Title
        title = QLabel("🫁 Guided Breathing Exercise")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Technique selector
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(QLabel("Technique:"))
        self.combo = QComboBox()
        for name, info in TECHNIQUES.items():
            self.combo.addItem(f"{name}  —  {info['desc']}")
        self.combo.setFixedWidth(350)
        ctrl_layout.addWidget(self.combo)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        # Circle
        self.circle = BreathCircle()
        layout.addWidget(self.circle, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status
        self.status_label = QLabel("Press Start to begin")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #b2bec3;")
        layout.addWidget(self.status_label)

        # Counter
        self.counter_label = QLabel("")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00d2d3;")
        layout.addWidget(self.counter_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_start = QPushButton("▶  Start Exercise")
        self.btn_start.setObjectName("btn_green")
        self.btn_start.setFixedWidth(200)
        self.btn_start.clicked.connect(self.toggle_exercise)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Countdown timer for seconds
        self._seconds_left = 0
        self._sec_timer = QTimer()
        self._sec_timer.setInterval(1000)
        self._sec_timer.timeout.connect(self._tick_second)

    def toggle_exercise(self):
        if self.is_running:
            self._stop()
        else:
            self._start()

    def _get_technique(self):
        idx = self.combo.currentIndex()
        name = list(TECHNIQUES.keys())[idx]
        return TECHNIQUES[name]

    def _start(self):
        self.is_running = True
        self.cycles_done = 0
        self.btn_start.setText("⏹  Stop")
        self.btn_start.setObjectName("btn_danger")
        self.btn_start.setStyleSheet("")  # trigger re-style
        self.current_phase = 0
        self._run_phase()

    def _stop(self):
        self.is_running = False
        self.phase_timer.stop()
        self._sec_timer.stop()
        self.btn_start.setText("▶  Start Exercise")
        self.btn_start.setObjectName("btn_green")
        self.btn_start.setStyleSheet("")
        self.circle.set_phase("Ready", "#00d2d3")
        self.counter_label.setText("")
        self.status_label.setText("Press Start to begin")

        # Animate circle back to small
        anim = QPropertyAnimation(self.circle, b"radius")
        anim.setDuration(500)
        anim.setStartValue(self.circle.radius)
        anim.setEndValue(40)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._current_anim = anim

    def _run_phase(self):
        if not self.is_running:
            return
        tech = self._get_technique()
        phases = [
            ("Breathe In",  tech["inhale"], "#00d2d3", 40, 100),
            ("Hold",        tech["hold"],   "#fdcb6e", 100, 100),
            ("Breathe Out", tech["exhale"], "#a29bfe", 100, 40),
        ]

        phase_name, duration_sec, color, start_r, end_r = phases[self.current_phase]

        self.circle.set_phase(phase_name, color)
        self.status_label.setText(f"Cycle {self.cycles_done + 1}/{self.total_cycles}  —  {phase_name}")
        self._seconds_left = duration_sec
        self.counter_label.setText(str(self._seconds_left))
        self._sec_timer.start()

        # Animate circle radius
        anim = QPropertyAnimation(self.circle, b"radius")
        anim.setDuration(duration_sec * 1000)
        anim.setStartValue(start_r)
        anim.setEndValue(end_r)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.start()
        self._current_anim = anim  # prevent garbage collection

        self.phase_timer.start(duration_sec * 1000)

    def _tick_second(self):
        self._seconds_left -= 1
        if self._seconds_left >= 0:
            self.counter_label.setText(str(self._seconds_left))
        else:
            self._sec_timer.stop()

    def _next_phase(self):
        self.phase_timer.stop()
        self._sec_timer.stop()
        self.current_phase += 1
        if self.current_phase >= 3:
            self.current_phase = 0
            self.cycles_done += 1
            if self.cycles_done >= self.total_cycles:
                self._finish()
                return
        self._run_phase()

    def _finish(self):
        self.is_running = False
        self.circle.set_phase("Great Job! 🎉", "#00b894")
        self.counter_label.setText("")
        self.status_label.setText(f"You completed {self.total_cycles} cycles. Well done!")
        self.btn_start.setText("▶  Start Again")
        self.btn_start.setObjectName("btn_green")
        self.btn_start.setStyleSheet("")
