"""
LagForge Test Suite (v1.101)
Verifies core engine math, Gaussian jitter, packet drop probability, UI widgets, and profile serialization.
"""

import sys
import os
import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine import PacketDelayEngine
from ui.custom_controls import LatencySliderWidget, SecondarySliderWidget, StatusIndicatorWidget
from ui.pill_switch import PillSwitch
from ui.sparkline import SparklineWidget
from ui.main_window import MainWindow
from ui.profile_dialog import ProfileManagerDialog
from config_manager import ConfigManager, DEFAULT_CONFIG


@pytest.fixture(scope="session")
def qapp():
    """Initializes QApplication instance for headless Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestEngineV101:
    def test_initial_state_and_properties(self, qapp):
        engine = PacketDelayEngine(filter_rule="!loopback")
        assert engine.filter_rule == "!loopback"
        assert not engine.is_active
        assert engine.target_ping_ms == 325.0
        assert engine.jitter_ms == 0.0
        assert engine.packet_loss_pct == 0.0

    def test_jitter_properties_and_calculation(self, qapp):
        engine = PacketDelayEngine()
        engine.target_ping_ms = 100.0
        engine.jitter_ms = 20.0
        assert engine.jitter_ms == 20.0

        # Sample multiple jitter values to ensure bounded Gaussian variance
        samples = [engine.calculate_effective_latency_ms() for _ in range(100)]
        for s in samples:
            assert s >= 0.0
            # Jitter is clamped to [-jitter_ms, +jitter_ms]
            assert 70.0 <= s <= 130.0

    def test_packet_drop_rates(self, qapp):
        engine = PacketDelayEngine()
        engine.packet_loss_pct = 0.0
        assert not any(engine.should_drop_packet() for _ in range(100))

        engine.packet_loss_pct = 100.0  # Clamped to 25.0 max
        assert engine.packet_loss_pct == 25.0

        # With 25% drop rate, sample 500 trials
        drops = sum(1 for _ in range(500) if engine.should_drop_packet())
        drop_rate = drops / 500.0
        # Expected ~0.25 (allow stochastic confidence interval [0.15, 0.35])
        assert 0.15 <= drop_rate <= 0.35

    def test_engine_lifecycle(self, qapp):
        engine = PacketDelayEngine()
        started_signal_received = []
        stopped_signal_received = []

        engine.started.connect(lambda: started_signal_received.append(True))
        engine.stopped.connect(lambda: stopped_signal_received.append(True))

        engine.start(target_ping_ms=200.0, jitter_ms=10.0, packet_loss_pct=5.0)
        assert engine.is_active
        assert engine.target_ping_ms == 200.0
        assert engine.jitter_ms == 10.0
        assert engine.packet_loss_pct == 5.0
        assert len(started_signal_received) == 1

        engine.stop()
        assert not engine.is_active
        assert len(stopped_signal_received) == 1


class TestUIComponentsV101:
    def test_secondary_slider(self, qapp):
        slider = SecondarySliderWidget(label="Jitter", min_val=0.0, max_val=100.0, initial_val=0.0, unit="ms")
        assert slider.value == 0.0

        values = []
        slider.valueChanged.connect(values.append)

        slider.setValue(25.0)
        assert slider.value == 25.0
        assert values == [25.0]

        slider.setValue(150.0)
        assert slider.value == 100.0

    def test_pill_switch_pulsing(self, qapp):
        switch = PillSwitch()
        assert not switch.is_active

        switch.set_active(True, animate=False)
        assert switch.is_active
        assert switch._pulse_timer.isActive()

        switch.set_active(False, animate=False)
        assert not switch.is_active
        assert not switch._pulse_timer.isActive()

    def test_profile_dialog(self, qapp):
        current_cfg = {"ping": 120, "jitter": 10.0, "loss": 2.0}
        profiles = [{"name": "TestProfile", "ping": 100, "jitter": 5.0, "loss": 1.0}]
        dlg = ProfileManagerDialog(current_cfg, profiles)
        assert dlg.list_widget.count() == 1

        # Add new profile
        dlg.txt_profile_name.setText("NewCustom")
        dlg._on_save_clicked()
        assert dlg.list_widget.count() == 2
        assert any(p["name"] == "NewCustom" for p in dlg.profiles)


class TestConfigManager:
    def test_config_load_save(self, tmp_path):
        cfg_file = os.path.join(tmp_path, "test_config.json")
        mgr = ConfigManager(config_path=cfg_file)

        # Load default
        cfg = mgr.load_config()
        assert cfg["version"] == "1.101"

        # Save modification
        cfg["ping"] = 450
        mgr.save_config(cfg)

        # Reload
        loaded = mgr.load_config()
        assert loaded["ping"] == 450
