"""
LagForge - Obsidian Dark Glassmorphism Stylesheet
Curated color tokens and QSS for high-DPI desktop rendering.
"""

COLORS = {
    "bg_base": "#090A0F",
    "card_bg": "#13151E",
    "card_bg_hover": "#181C2B",
    "card_border": "#212638",
    "card_border_glow": "#00F0FF",
    "text_primary": "#FFFFFF",
    "text_secondary": "#9CA3AF",
    "text_muted": "#525A70",
    "accent_cyan": "#00F0FF",
    "accent_cyan_glow": "rgba(0, 240, 255, 0.35)",
    "accent_emerald": "#10B981",
    "accent_emerald_glow": "rgba(16, 185, 129, 0.4)",
    "slider_groove": "#1A1E2C",
    "slider_handle": "#00F0FF",
    "slider_handle_border": "#FFFFFF",
    "preset_active_bg": "#102534",
    "preset_active_border": "#00F0FF",
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
    font-size: 13px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel.big-metric {{
    font-size: 40px;
    font-weight: 800;
    color: {COLORS['text_primary']};
    letter-spacing: -1px;
}}

QLabel.medium-metric {{
    font-size: 26px;
    font-weight: 800;
    color: {COLORS['text_primary']};
    letter-spacing: -0.5px;
}}

QLabel.split-metric {{
    font-size: 16px;
    font-weight: 700;
    color: {COLORS['text_primary']};
}}

/* Preset Buttons */
QPushButton.preset-btn {{
    background-color: {COLORS['card_bg']};
    border: 1px solid {COLORS['card_border']};
    border-radius: 10px;
    color: {COLORS['text_primary']};
    font-size: 16px;
    font-weight: 700;
    padding: 12px 18px;
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

/* Modern Horizontal Slider */
QSlider::groove:horizontal {{
    height: 6px;
    background: {COLORS['slider_groove']};
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #00A3FF, stop:1 {COLORS['accent_cyan']});
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['accent_cyan']};
    border: 2px solid #FFFFFF;
    width: 20px;
    height: 20px;
    margin: -7px 0;
    border-radius: 10px;
}}

QSlider::handle:horizontal:hover {{
    background: #55FFFF;
    border: 2px solid #FFFFFF;
    width: 22px;
    height: 22px;
    margin: -8px 0;
    border-radius: 11px;
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
