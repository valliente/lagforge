"""
LagForge - Main Entry Point & Admin Elevation Wrapper (v1.101)
Obsidian Glassmorphic Latency Control App with Global Hotkey and Tray Integration.
"""

import sys
import os
import ctypes
import signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont

from ui.main_window import MainWindow
from hotkey_manager import GlobalHotkeyManager
from config_manager import ConfigManager


def is_admin() -> bool:
    """Checks if current process has Windows Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def elevate_privileges() -> bool:
    """Relaunches current script with elevated Administrator rights via UAC prompt."""
    if is_admin():
        return True

    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        if ret > 32:
            sys.exit(0)
    except Exception as e:
        print(f"Elevation request failed: {e}")

    return False


def main():
    skip_elevation = "--no-elevation" in sys.argv or "--dry-run" in sys.argv

    admin_status = is_admin()
    if not admin_status and not skip_elevation:
        elevate_privileges()

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("LagForge")
    app.setOrganizationName("LagForge")
    app.setQuitOnLastWindowClosed(False)

    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Load Configuration
    config_mgr = ConfigManager()
    cfg = config_mgr.load_config()

    window = MainWindow(is_admin=is_admin())
    
    # Apply loaded config values
    if "ping" in cfg:
        window.slider.setValue(int(cfg["ping"]))
    if "jitter" in cfg:
        window.jitter_slider.setValue(float(cfg["jitter"]))
    if "loss" in cfg:
        window.loss_slider.setValue(float(cfg["loss"]))
    if "profiles" in cfg and isinstance(cfg["profiles"], list):
        window.saved_profiles = cfg["profiles"]

    # Start Global Hotkey Listener
    hotkey_mgr = GlobalHotkeyManager()
    hotkey_mgr.hotkey_triggered.connect(window.toggle_active_state)
    hotkey_mgr.start()

    window.show()

    exit_code = app.exec()

    # Save Configuration on Exit
    save_data = {
        "version": "1.101",
        "ping": window.current_ping,
        "jitter": window.current_jitter,
        "loss": window.current_loss,
        "profiles": window.saved_profiles,
    }
    config_mgr.save_config(save_data)
    hotkey_mgr.stop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
