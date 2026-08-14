"""
LagForge - Main Window
PySide6 Obsidian Dark Glassmorphism Application Interface.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QButtonGroup,
    QGraphicsDropShadowEffect,
    QMessageBox,
)

from .styles import MAIN_STYLESHEET, COLORS
from .sparkline import SparklineWidget
from .pill_switch import PillSwitch
from .custom_controls import LagForgeLogo, LatencySliderWidget, StatusIndicatorWidget
from engine import PacketDelayEngine


class MainWindow(QMainWindow):
    """
    Main Application Window for LagForge.
    """

    def __init__(self, is_admin: bool = True):
        super().__init__()
        self.is_admin = is_admin
        self.current_ping = 325

        # Initialize Packet Delay Engine
        self.engine = PacketDelayEngine(filter_rule="!loopback", parent=self)

        self._setup_window()
        self._init_ui()
        self._connect_signals()

        # Update initial display values
        self._update_latency_display(self.current_ping)

    def _setup_window(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("LagForge - Global Latency Control")
        self.resize(880, 480)
        self.setMinimumSize(820, 440)
        self.setStyleSheet(MAIN_STYLESHEET)

    def _init_ui(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(24, 20, 24, 18)
        root_layout.setSpacing(18)

        # -------------------------------------------------------------
        # 1. HEADER BAR
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        # Logo and Titles
        self.logo_widget = LagForgeLogo(38, self)
        header_layout.addWidget(self.logo_widget)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("LagForge")
        title_label.setObjectName("AppTitle")
        title_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;")

        subtitle_label = QLabel("Global Latency Control")
        subtitle_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #9CA3AF;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addLayout(title_layout)

        header_layout.addStretch()

        # Right: Pill Switch
        self.pill_switch = PillSwitch(self)
        header_layout.addWidget(self.pill_switch)

        root_layout.addLayout(header_layout)

        # -------------------------------------------------------------
        # 2. MAIN BODY (3 Columns: Presets, Latency Slider, Telemetry)
        # -------------------------------------------------------------
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # --- LEFT PANEL: PRESETS ---
        presets_card = QFrame()
        presets_card.setProperty("class", "glass-card")
        presets_card.setStyleSheet(
            f"background-color: {COLORS['card_bg']}; border: 1px solid {COLORS['card_border']}; border-radius: 12px;"
        )
        presets_layout = QVBoxLayout(presets_card)
        presets_layout.setContentsMargins(14, 16, 14, 16)
        presets_layout.setSpacing(10)

        self.preset_group = QButtonGroup(self)
        self.preset_group.setExclusive(True)
        self.preset_buttons = {}

        for ms in (50, 100, 200, 500):
            btn = QPushButton(f"+{ms}ms")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #151824;
                    border: 1px solid {COLORS['card_border']};
                    border-radius: 10px;
                    color: #FFFFFF;
                    font-size: 15px;
                    font-weight: 700;
                    padding: 14px 18px;
                }}
                QPushButton:hover {{
                    background-color: #1A1F30;
                    border: 1px solid {COLORS['accent_cyan']};
                    color: {COLORS['accent_cyan']};
                }}
                QPushButton:checked {{
                    background-color: {COLORS['preset_active_bg']};
                    border: 1.5px solid {COLORS['accent_cyan']};
                    color: {COLORS['accent_cyan']};
                }}
            """)
            btn.clicked.connect(lambda checked, val=ms: self._on_preset_clicked(val))
            self.preset_group.addButton(btn)
            self.preset_buttons[ms] = btn
            presets_layout.addWidget(btn)

        body_layout.addWidget(presets_card, stretch=2)

        # --- CENTER PANEL: CONTROL & SLIDER ---
        control_card = QFrame()
        control_card.setProperty("class", "glass-card")
        control_card.setStyleSheet(
            f"background-color: {COLORS['card_bg']}; border: 1px solid {COLORS['card_border']}; border-radius: 12px;"
        )
        control_layout = QVBoxLayout(control_card)
        control_layout.setContentsMargins(20, 24, 20, 20)
        control_layout.setSpacing(16)

        # Slider Widget with ticks
        self.slider = LatencySliderWidget(min_val=0, max_val=1000, initial_val=self.current_ping, parent=self)
        control_layout.addWidget(self.slider)

        control_layout.addStretch()

        # Large Readout display
        readout_layout = QVBoxLayout()
        readout_layout.setSpacing(2)
        readout_layout.setAlignment(Qt.AlignCenter)

        self.lbl_big_ping = QLabel(f"+{self.current_ping} ms")
        self.lbl_big_ping.setAlignment(Qt.AlignCenter)
        self.lbl_big_ping.setStyleSheet("font-size: 42px; font-weight: 800; color: #FFFFFF; letter-spacing: -1px;")

        self.lbl_ping_sub = QLabel("Total Added Ping")
        self.lbl_ping_sub.setAlignment(Qt.AlignCenter)
        self.lbl_ping_sub.setStyleSheet("font-size: 13px; font-weight: 500; color: #9CA3AF;")

        readout_layout.addWidget(self.lbl_big_ping)
        readout_layout.addWidget(self.lbl_ping_sub)
        control_layout.addLayout(readout_layout)

        control_layout.addStretch()

        body_layout.addWidget(control_card, stretch=5)

        # --- RIGHT PANEL: TELEMETRY STACK ---
        telemetry_container = QVBoxLayout()
        telemetry_container.setSpacing(10)

        # 1. Delayed Packets Card
        pkt_card = QFrame()
        pkt_card.setStyleSheet(
            f"background-color: {COLORS['card_bg']}; border: 1px solid {COLORS['card_border']}; border-radius: 12px;"
        )
        pkt_layout = QVBoxLayout(pkt_card)
        pkt_layout.setContentsMargins(16, 12, 16, 12)
        pkt_layout.setSpacing(2)

        lbl_pkt_title = QLabel("Packets Delayed")
        lbl_pkt_title.setStyleSheet("font-size: 11px; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px;")
        
        self.lbl_pkt_count = QLabel("0")
        self.lbl_pkt_count.setStyleSheet("font-size: 26px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;")

        pkt_layout.addWidget(lbl_pkt_title)
        pkt_layout.addWidget(self.lbl_pkt_count)
        telemetry_container.addWidget(pkt_card)

        # 2. Sparkline Graph Card
        spark_card = QFrame()
        spark_card.setStyleSheet(
            f"background-color: {COLORS['card_bg']}; border: 1px solid {COLORS['card_border']}; border-radius: 12px;"
        )
        spark_layout = QVBoxLayout(spark_card)
        spark_layout.setContentsMargins(12, 8, 12, 8)
        self.sparkline = SparklineWidget(max_points=50, parent=self)
        spark_layout.addWidget(self.sparkline)
        telemetry_container.addWidget(spark_card)

        # 3. Split Inbound / Outbound Readout Card
        split_card = QFrame()
        split_card.setStyleSheet(
            f"background-color: {COLORS['card_bg']}; border: 1px solid {COLORS['card_border']}; border-radius: 12px;"
        )
        split_layout = QHBoxLayout(split_card)
        split_layout.setContentsMargins(14, 10, 14, 10)
        split_layout.setSpacing(10)

        # Inbound section
        in_layout = QVBoxLayout()
        in_layout.setSpacing(2)
        lbl_in_title = QLabel("Inbound:")
        lbl_in_title.setStyleSheet("font-size: 11px; font-weight: 500; color: #9CA3AF;")
        self.lbl_in_val = QLabel("162.5ms")
        self.lbl_in_val.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        in_layout.addWidget(lbl_in_title)
        in_layout.addWidget(self.lbl_in_val)
        split_layout.addLayout(in_layout)

        # Vertical Divider with subtle cyan accent
        v_divider = QFrame()
        v_divider.setFrameShape(QFrame.VLine)
        v_divider.setStyleSheet(f"background-color: {COLORS['accent_cyan']}; max-width: 2px; border-radius: 1px;")
        split_layout.addWidget(v_divider)

        # Outbound section
        out_layout = QVBoxLayout()
        out_layout.setSpacing(2)
        lbl_out_title = QLabel("Outbound:")
        lbl_out_title.setStyleSheet("font-size: 11px; font-weight: 500; color: #9CA3AF;")
        self.lbl_out_val = QLabel("162.5ms")
        self.lbl_out_val.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        out_layout.addWidget(lbl_out_title)
        out_layout.addWidget(self.lbl_out_val)
        split_layout.addLayout(out_layout)

        telemetry_container.addWidget(split_card)

        body_layout.addLayout(telemetry_container, stretch=3)
        root_layout.addLayout(body_layout)

        # -------------------------------------------------------------
        # 3. FOOTER STATUS BAR
        # -------------------------------------------------------------
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(2, 4, 2, 0)
        footer_layout.setSpacing(8)

        self.status_dots = StatusIndicatorWidget(self)
        footer_layout.addWidget(self.status_dots)

        self.lbl_rule = QLabel("Rule: !loopback connection.")
        self.lbl_rule.setStyleSheet("font-family: 'Consolas', monospace; font-size: 12px; color: #9CA3AF;")
        footer_layout.addWidget(self.lbl_rule)

        footer_layout.addStretch()

        if not self.is_admin:
            admin_notice = QLabel("⚠ Running without Admin rights (Read-Only / Simulation)")
            admin_notice.setStyleSheet("font-size: 11px; color: #F59E0B;")
            footer_layout.addWidget(admin_notice)

        root_layout.addLayout(footer_layout)

    def _connect_signals(self):
        # Slider & Presets
        self.slider.valueChanged.connect(self._on_slider_changed)

        # Pill switch
        self.pill_switch.toggled.connect(self._on_switch_toggled)

        # Engine Telemetry
        self.engine.telemetry_updated.connect(self._on_telemetry_received)
        self.engine.error_occurred.connect(self._on_engine_error)
        self.engine.started.connect(lambda: self.status_dots.set_active(True))
        self.engine.stopped.connect(lambda: self.status_dots.set_active(False))

    def _on_slider_changed(self, val: int):
        self.current_ping = val
        self._update_latency_display(val)

        # Update preset checked state if matching
        for ms, btn in self.preset_buttons.items():
            btn.setChecked(ms == val)

        # Update running engine dynamically
        self.engine.target_ping_ms = float(val)

    def _on_preset_clicked(self, ms: int):
        self.slider.setValue(ms)

    def _update_latency_display(self, ping_ms: int):
        self.lbl_big_ping.setText(f"+{ping_ms} ms")
        half_ms = ping_ms / 2.0
        self.lbl_in_val.setText(f"{half_ms:.1f}ms")
        self.lbl_out_val.setText(f"{half_ms:.1f}ms")

    def _on_switch_toggled(self, active: bool):
        if active:
            self.engine.start(target_ping_ms=float(self.current_ping))
            self.status_dots.set_active(True)
        else:
            self.engine.stop()
            self.status_dots.set_active(False)
            self.sparkline.reset()

    def _on_telemetry_received(self, total: int, pps: float, in_ms: float, out_ms: float, spark_val: float):
        self.lbl_pkt_count.setText(f"{total:,}")
        self.sparkline.add_data_point(spark_val)
        self.lbl_in_val.setText(f"{in_ms:.1f}ms")
        self.lbl_out_val.setText(f"{out_ms:.1f}ms")

    def _on_engine_error(self, err_msg: str):
        self.pill_switch.set_active(False)
        self.status_dots.set_active(False)
        QMessageBox.warning(self, "LagForge Engine", err_msg)

    def closeEvent(self, event):
        """Ensure clean shutdown of the packet delay engine on window close."""
        self.engine.stop()
        super().closeEvent(event)
