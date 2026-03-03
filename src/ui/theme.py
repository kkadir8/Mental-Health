"""
Modern Theme System — Professional dark/light themes for the application.
Uses QSS (Qt Style Sheets) for consistent, polished appearance.
"""

# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
COLORS = {
    "bg_primary":       "#1a1a2e",
    "bg_secondary":     "#16213e",
    "bg_card":          "#0f3460",
    "bg_input":         "#1a1a3e",
    "accent":           "#e94560",
    "accent_hover":     "#ff6b81",
    "accent_green":     "#00d2d3",
    "accent_purple":    "#a29bfe",
    "accent_orange":    "#fdcb6e",
    "accent_blue":      "#74b9ff",
    "text_primary":     "#ffffff",
    "text_secondary":   "#b2bec3",
    "text_muted":       "#636e72",
    "border":           "#2d3436",
    "success":          "#00b894",
    "warning":          "#fdcb6e",
    "danger":           "#e74c3c",
    "info":             "#74b9ff",
    "sidebar_bg":       "#0a0a1a",
    "sidebar_hover":    "#1a1a3e",
    "sidebar_active":   "#e94560",
    "header_gradient_1":"#1a1a2e",
    "header_gradient_2":"#16213e",
}


def get_main_stylesheet():
    """Returns the complete QSS stylesheet for the application."""
    return f"""
    /* ===== GLOBAL ===== */
    QMainWindow {{
        background-color: {COLORS['bg_primary']};
    }}
    QWidget {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
        font-size: 13px;
    }}

    /* ===== LABELS ===== */
    QLabel {{
        color: {COLORS['text_primary']};
        background: transparent;
    }}
    QLabel#header_title {{
        font-size: 26px;
        font-weight: bold;
        color: {COLORS['text_primary']};
    }}
    QLabel#header_subtitle {{
        font-size: 12px;
        color: {COLORS['text_secondary']};
        font-style: italic;
    }}
    QLabel#section_title {{
        font-size: 18px;
        font-weight: bold;
        color: {COLORS['accent']};
        padding: 5px 0px;
    }}
    QLabel#card_title {{
        font-size: 14px;
        font-weight: bold;
        color: {COLORS['accent_green']};
    }}
    QLabel#stat_value {{
        font-size: 28px;
        font-weight: bold;
        color: {COLORS['text_primary']};
    }}
    QLabel#stat_label {{
        font-size: 11px;
        color: {COLORS['text_secondary']};
    }}
    QLabel#mood_emoji {{
        font-size: 48px;
        background: transparent;
    }}
    QLabel#daily_tip {{
        font-size: 13px;
        color: {COLORS['accent_orange']};
        padding: 8px;
        background: rgba(253, 203, 110, 0.1);
        border-radius: 8px;
        border-left: 3px solid {COLORS['accent_orange']};
    }}

    /* ===== BUTTONS ===== */
    QPushButton {{
        background-color: {COLORS['accent']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['accent_hover']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['accent']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['text_muted']};
        color: {COLORS['border']};
    }}
    QPushButton#btn_green {{
        background-color: {COLORS['success']};
    }}
    QPushButton#btn_green:hover {{
        background-color: #00cec9;
    }}
    QPushButton#btn_purple {{
        background-color: {COLORS['accent_purple']};
    }}
    QPushButton#btn_purple:hover {{
        background-color: #6c5ce7;
    }}
    QPushButton#btn_blue {{
        background-color: {COLORS['accent_blue']};
    }}
    QPushButton#btn_blue:hover {{
        background-color: #0984e3;
    }}
    QPushButton#btn_danger {{
        background-color: {COLORS['danger']};
    }}
    QPushButton#btn_danger:hover {{
        background-color: #c0392b;
    }}
    QPushButton#sidebar_btn {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        border: none;
        border-radius: 12px;
        padding: 14px 18px;
        text-align: left;
        font-size: 14px;
        font-weight: normal;
    }}
    QPushButton#sidebar_btn:hover {{
        background-color: {COLORS['sidebar_hover']};
        color: {COLORS['text_primary']};
    }}
    QPushButton#sidebar_btn_active {{
        background-color: {COLORS['accent']};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 18px;
        text-align: left;
        font-size: 14px;
        font-weight: bold;
    }}

    /* ===== TEXT INPUTS ===== */
    QTextEdit {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border']};
        border-radius: 10px;
        padding: 12px;
        font-size: 14px;
        selection-background-color: {COLORS['accent']};
    }}
    QTextEdit:focus {{
        border-color: {COLORS['accent']};
    }}
    QLineEdit {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border-color: {COLORS['accent']};
    }}

    /* ===== COMBO BOX ===== */
    QComboBox {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        min-width: 160px;
    }}
    QComboBox:hover {{
        border-color: {COLORS['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['accent']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
    }}

    /* ===== TAB WIDGET ===== */
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['bg_primary']};
        border-radius: 4px;
    }}
    QTabBar::tab {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_secondary']};
        padding: 10px 24px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-size: 13px;
    }}
    QTabBar::tab:selected {{
        background-color: {COLORS['accent']};
        color: white;
        font-weight: bold;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['sidebar_hover']};
        color: {COLORS['text_primary']};
    }}

    /* ===== PROGRESS BAR ===== */
    QProgressBar {{
        background-color: {COLORS['bg_secondary']};
        border: none;
        border-radius: 6px;
        height: 12px;
        text-align: center;
        color: white;
        font-size: 10px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['accent']}, stop:1 {COLORS['accent_purple']});
        border-radius: 6px;
    }}

    /* ===== TABLE ===== */
    QTableWidget {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        gridline-color: {COLORS['border']};
    }}
    QTableWidget::item {{
        padding: 4px;
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['accent']};
    }}
    QHeaderView::section {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        padding: 8px;
        border: none;
        font-weight: bold;
    }}

    /* ===== SCROLL BARS ===== */
    QScrollBar:vertical {{
        background-color: {COLORS['bg_primary']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLORS['text_muted']};
        border-radius: 5px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['accent']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background-color: {COLORS['bg_primary']};
        height: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['text_muted']};
        border-radius: 5px;
        min-width: 20px;
    }}

    /* ===== SPLITTER ===== */
    QSplitter::handle {{
        background-color: {COLORS['border']};
    }}

    /* ===== LIST WIDGET ===== */
    QListWidget {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 8px;
        border-radius: 4px;
        margin: 2px;
    }}
    QListWidget::item:selected {{
        background-color: {COLORS['accent']};
    }}
    QListWidget::item:hover:!selected {{
        background-color: {COLORS['sidebar_hover']};
    }}

    /* ===== STATUS BAR ===== */
    QStatusBar {{
        background-color: {COLORS['sidebar_bg']};
        color: {COLORS['text_secondary']};
        font-size: 12px;
    }}

    /* ===== TOOLTIP ===== */
    QToolTip {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
        padding: 6px;
    }}

    /* ===== MESSAGE BOX ===== */
    QMessageBox {{
        background-color: {COLORS['bg_primary']};
    }}
    QMessageBox QLabel {{
        color: {COLORS['text_primary']};
    }}

    /* ===== CARD WIDGET ===== */
    QFrame#card {{
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 16px;
    }}
    QFrame#card_accent {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['accent']};
        border-radius: 12px;
        padding: 16px;
    }}
    QFrame#response_card {{
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 20px;
    }}
    QFrame#crisis_card {{
        background-color: rgba(231, 76, 60, 0.15);
        border: 2px solid {COLORS['danger']};
        border-radius: 12px;
        padding: 16px;
    }}
    QFrame#sidebar_frame {{
        background-color: {COLORS['sidebar_bg']};
        border-right: 1px solid {COLORS['border']};
    }}
    """


def card_style(accent_color=None):
    """Generate inline card style with optional accent border."""
    border_color = accent_color or COLORS['border']
    return f"""
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 16px;
    """


def stat_card_style():
    return f"""
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 12px;
    """
