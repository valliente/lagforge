"""
LagForge - Global Hotkey Manager (v1.101)
Registers system-wide hotkeys (F8 and Ctrl+Shift+L) using Windows User32 API.
"""

import sys
import ctypes
import threading
from ctypes import wintypes
from PySide6.QtCore import QObject, Signal

# Win32 Constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
VK_F8 = 0x77
VK_L = 0x4C

HOTKEY_ID_F8 = 101
HOTKEY_ID_CTRL_SHIFT_L = 102


class GlobalHotkeyManager(QObject):
    """
    Background worker that listens for global hotkey presses and signals the main UI.
    """

    hotkey_triggered = Signal()

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._thread = None
        self._stop_event = threading.Event()
        self._thread_id = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._hotkey_loop, name="LagForge-HotkeyThread", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread_id and sys.platform == "win32":
            try:
                # Post WM_QUIT to unblock GetMessageW
                ctypes.windll.user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2)

    def _hotkey_loop(self):
        if sys.platform != "win32":
            return

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        self._thread_id = kernel32.GetCurrentThreadId()

        # Register F8
        user32.RegisterHotKey(None, HOTKEY_ID_F8, MOD_NOREPEAT, VK_F8)
        # Register Ctrl+Shift+L
        user32.RegisterHotKey(None, HOTKEY_ID_CTRL_SHIFT_L, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_L)

        msg = wintypes.MSG()
        try:
            while not self._stop_event.is_set():
                # GetMessageW blocks until a message is posted to this thread
                res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res <= 0:
                    break

                if msg.message == WM_HOTKEY:
                    if msg.wParam in (HOTKEY_ID_F8, HOTKEY_ID_CTRL_SHIFT_L):
                        self.hotkey_triggered.emit()

                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID_F8)
            user32.UnregisterHotKey(None, HOTKEY_ID_CTRL_SHIFT_L)
