"""
LagForge - Obsidian Dark Glassmorphism Stylesheet (v1.101)
Curated color tokens, frosted card containers, and QSS for high-DPI desktop rendering.
"""

COLORS = {
    "bg_base": "#090A0F",
    "card_bg": "#13151E",
    "card_bg_hover": "#181C2B",
    "card_border": "#212638",
    "card_border_glow": "#00F0FF",
    "card_border_glow_subtle": "rgba(0, 240, 255, 0.2)",
    "text_primary": "#FFFFFF",
    "text_secondary": "#9CA3AF",
    "text_muted": "#525A70",
    "accent_cyan": "#00F0FF",
    "accent_cyan_glow": "rgba(0, 240, 255, 0.35)",
    "accent_emerald": "#10B981",
    "accent_emerald_glow": "rgba(16, 185, 129, 0.4)",
    "accent_amber": "#F59E0B",
    "accent_rose": "#F43F5E",
    "slider_groove": "#1A1E2C",
    "slider_handle": "#00F0FF",
    "slider_handle_border": "#FFFFFF",
    "preset_active_bg": "#102534",
    "preset_active_border": "#00F0FF",
    "dialog_bg": "#0D0F17",
}

MAIN_STYLESHEET = f"""
/* Global Window */
QMainWindow {{
    background-color: {COLORS['bg_base']};
}}

QWidget#CentralWidget {{
    background-color: {COLORS['bg_base']};
}}

QWidget {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Roboto, sans-serif;
    color: {COLORS['text_primary']};
}}

/* Card Containers (Frosted Glass Obsidian look) */
QFrame.glass-card {{
    background-color: {COLORS['card_bg']};
    border: 1px solid {COLORS['card_border']};
    border-radius: 12px;
}}

QFrame.glass-card-hover:hover {{
    border: 1px solid {COLORS['card_border_glow']};
}}

/* Typography */
QLabel.heading-title {{
    font-size: 22px;
    font-weight: 800;
    color: {COLORS['text_primary']};
    letter-spacing: -0.5px;
}}

QLabel.sub-label {{
    font-size: 12px;
    font-weight: 500;
    color: {COLORS['text_secondary']};
}}

QLabel.card-title {{
    font-size: 11px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel.big-metric {{
    font-size: 38px;
    font-weight: 800;
    color: {COLORS['text_primary']};
    letter-spacing: -1px;
}}

QLabel.medium-metric {{
    font-size: 24px;
    font-weight: 800;
    color: {COLORS['text_primary']};
    letter-spacing: -0.5px;
}}

QLabel.small-metric {{
    font-size: 14px;
    font-weight: 700;
    color: {COLORS['text_primary']};
}}

/* Preset Buttons */
QPushButton.preset-btn {{
    background-color: {COLORS['card_bg']};
    border: 1px solid {COLORS['card_border']};
    border-radius: 10px;
    color: {COLORS['text_primary']};
    font-size: 15px;
    font-weight: 700;
    padding: 12px 16px;
    text-align: center;
}}

QPushButton.preset-btn:hover {{
    background-color: {COLORS['card_bg_hover']};
    border: 1px solid {COLORS['accent_cyan']};
    color: {COLORS['accent_cyan']};
}}

QPushButton.preset-btn:checked, QPushButton.preset-btn.active {{
    background-color: {COLORS['preset_active_bg']};
    border: 1.5px solid {COLORS['preset_active_border']};
    color: {COLORS['accent_cyan']};
}}

QPushButton.preset-btn:pressed {{
    background-color: #0E1F2C;
}}

/* Action / Utility Buttons */
QPushButton.action-btn {{
    background-color: #161A28;
    border: 1px solid {COLORS['card_border']};
    border-radius: 8px;
    color: {COLORS['text_primary']};
    font-size: 12px;
    font-weight: 600;
    padding: 6px 12px;
}}

QPushButton.action-btn:hover {{
    background-color: #20273D;
    border: 1px solid {COLORS['accent_cyan']};
    color: {COLORS['accent_cyan']};
}}

QPushButton.action-btn-primary {{
    background-color: #0088AA;
    border: 1px solid {COLORS['accent_cyan']};
    border-radius: 8px;
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
}}

QPushButton.action-btn-primary:hover {{
    background-color: #00AACC;
}}

/* Modern Horizontal Sliders */
QSlider::groove:horizontal {{
    height: 5px;
    background: {COLORS['slider_groove']};
    border-radius: 2.5px;
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #00A3FF, stop:1 {COLORS['accent_cyan']});
    border-radius: 2.5px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['accent_cyan']};
    border: 2px solid #FFFFFF;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: #55FFFF;
    border: 2px solid #FFFFFF;
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 9px;
}}

/* Dialog Styles */
QDialog {{
    background-color: {COLORS['dialog_bg']};
    border: 1px solid {COLORS['card_border']};
    border-radius: 12px;
}}

QLineEdit {{
    background-color: #151824;
    border: 1px solid {COLORS['card_border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: #FFFFFF;
    font-size: 13px;
}}

QLineEdit:focus {{
    border: 1px solid {COLORS['accent_cyan']};
}}

QListWidget {{
    background-color: #12141F;
    border: 1px solid {COLORS['card_border']};
    border-radius: 8px;
    color: #FFFFFF;
    padding: 6px;
}}

QListWidget::item {{
    padding: 8px 10px;
    border-radius: 6px;
}}

QListWidget::item:hover {{
    background-color: #1A1F30;
    color: {COLORS['accent_cyan']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['preset_active_bg']};
    color: {COLORS['accent_cyan']};
    border: 1px solid {COLORS['accent_cyan']};
}}

/* Tooltip */
QToolTip {{
    background-color: #1A1E2D;
    color: #FFFFFF;
    border: 1px solid #2B334B;
    border-radius: 6px;
    padding: 6px;
    font-size: 11px;
}}

/* Status indicator / Footer */
QLabel.footer-rule {{
    font-size: 12px;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    color: {COLORS['text_secondary']};
}}
"""
