"""
LagForge Test Suite
Verifies core engine math, queue management, custom UI controls, and signal routing.
"""

import sys
import os
import pytest
from PySide6.QtWidgets import QApplication

# Ensure scratch/lagforge is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine import PacketDelayEngine
from ui.custom_controls import LatencySliderWidget, StatusIndicatorWidget
from ui.pill_switch import PillSwitch
from ui.sparkline import SparklineWidget
from ui.main_window import MainWindow
from ui.styles import COLORS, MAIN_STYLESHEET


@pytest.fixture(scope="session")
def qapp():
    """Initializes QApplication instance for headless Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestEngine:
    def test_initial_state_and_properties(self, qapp):
        engine = PacketDelayEngine(filter_rule="!loopback")
        assert engine.filter_rule == "!loopback"
        assert not engine.is_active
        assert engine.target_ping_ms == 325.0

    def test_target_ping_clamping_and_math(self, qapp):
        engine = PacketDelayEngine()
        engine.target_ping_ms = 500.0
        assert engine.target_ping_ms == 500.0
        # Negative ping clamped to 0
        engine.target_ping_ms = -50.0
        assert engine.target_ping_ms == 0.0

    def test_engine_start_stop_lifecycle(self, qapp):
        engine = PacketDelayEngine()
        started_signal_received = []
        stopped_signal_received = []

        engine.started.connect(lambda: started_signal_received.append(True))
        engine.stopped.connect(lambda: stopped_signal_received.append(True))

        engine.start(target_ping_ms=200.0)
        assert engine.is_active
        assert engine.target_ping_ms == 200.0
        assert len(started_signal_received) == 1

        engine.stop()
        assert not engine.is_active
        assert len(stopped_signal_received) == 1


class TestUIComponents:
    def test_latency_slider(self, qapp):
        slider = LatencySliderWidget(min_val=0, max_val=1000, initial_val=100)
        assert slider.value == 100

        values = []
        slider.valueChanged.connect(values.append)

        slider.setValue(450)
        assert slider.value == 450
        assert values == [450]

        # Test clamping
        slider.setValue(2000)
        assert slider.value == 1000

        slider.setValue(-50)
        assert slider.value == 0

    def test_pill_switch(self, qapp):
        switch = PillSwitch()
        assert not switch.is_active

        states = []
        switch.toggled.connect(states.append)

        switch.set_active(True, animate=False)
        assert switch.is_active
        assert states == [True]

        switch.set_active(False, animate=False)
        assert not switch.is_active
        assert states == [True, False]

    def test_sparkline_widget(self, qapp):
        sparkline = SparklineWidget(max_points=30)
        assert len(sparkline.data_points) == 30
        assert all(v == 0.0 for v in sparkline.data_points)

        sparkline.add_data_point(15.5)
        assert sparkline.data_points[-1] == 15.5

        sparkline.reset()
        assert sparkline.data_points[-1] == 0.0

    def test_status_indicator(self, qapp):
        indicator = StatusIndicatorWidget()
        indicator.set_active(True)
        assert indicator._active
        indicator.set_active(False)
        assert not indicator._active


class TestMainWindow:
    def test_main_window_init_and_presets(self, qapp):
        window = MainWindow(is_admin=False)
        assert window.windowTitle() == "LagForge - Global Latency Control"
        assert window.current_ping == 325
        assert window.lbl_big_ping.text() == "+325 ms"
        assert window.lbl_in_val.text() == "162.5ms"
        assert window.lbl_out_val.text() == "162.5ms"

        # Preset test
        window._on_preset_clicked(100)
        assert window.slider.value == 100
        assert window.lbl_big_ping.text() == "+100 ms"
        assert window.lbl_in_val.text() == "50.0ms"
        assert window.lbl_out_val.text() == "50.0ms"

        # Slider adjustment test
        window.slider.setValue(500)
        assert window.current_ping == 500
        assert window.lbl_big_ping.text() == "+500 ms"
        assert window.lbl_in_val.text() == "250.0ms"
        assert window.lbl_out_val.text() == "250.0ms"

        # Safe close
        window.close()
