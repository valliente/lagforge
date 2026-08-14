"""
LagForge - Main Entry Point & Admin Elevation Wrapper
Obsidian Glassmorphic Latency Control App.
"""

import sys
import os
import ctypes
import signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon

from ui.main_window import MainWindow


def is_admin() -> bool:
    """Checks if current process has Windows Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def elevate_privileges():
    """Relaunches current script with elevated Administrator rights via UAC prompt."""
    if is_admin():
        return True

    # Re-launch with ShellExecuteW runas
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        # ShellExecute returns > 32 on success
        if ret > 32:
            sys.exit(0)
    except Exception as e:
        print(f"Elevation request failed: {e}")

    return False


def main():
    # Parse custom flags
    skip_elevation = "--no-elevation" in sys.argv or "--dry-run" in sys.argv

    admin_status = is_admin()
    if not admin_status and not skip_elevation:
        # Prompt for UAC Elevation
        elevate_privileges()
        # If user denied UAC, continue running in unprivileged / demo mode

    # Set High-DPI attributes before creating QApplication
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("LagForge")
    app.setOrganizationName("LagForge")

    # Set default modern UI font
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    # Enable graceful CTRL+C exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    window = MainWindow(is_admin=is_admin())
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
