"""
LagForge - Custom UI Controls (v1.101)
Custom widgets for Sliders (Latency, Jitter, Packet Loss), Geometric Logo, and Status Indicators.
"""

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QPainterPath,
    QLinearGradient,
    QBrush,
    QFont,
)
from PySide6.QtWidgets import QWidget


class LagForgeLogo(QWidget):
    """
    Renders the modern geometric layered diamond icon.
    """

    def __init__(self, size: int = 40, parent: QWidget = None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        s = float(min(self.width(), self.height()))
        pad = s * 0.1
        box = s - (pad * 2.0)

        # Background rounded badge
        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(pad, pad, box, box), s * 0.22, s * 0.22)
        
        bg_gradient = QLinearGradient(pad, pad, pad + box, pad + box)
        bg_gradient.setColorAt(0.0, QColor("#1C2234"))
        bg_gradient.setColorAt(1.0, QColor("#111420"))
        painter.fillPath(bg_path, QBrush(bg_gradient))

        border_pen = QPen(QColor("#2C364F"), 1.2)
        painter.setPen(border_pen)
        painter.drawPath(bg_path)

        # Geometric layered diamond / S-shape ribbon
        cx = s / 2.0
        cy = s / 2.0
        r = box * 0.32

        # Upper diamond segment
        path_top = QPainterPath()
        path_top.moveTo(cx, cy - r)
        path_top.lineTo(cx + r, cy)
        path_top.lineTo(cx, cy + (r * 0.3))
        path_top.lineTo(cx - (r * 0.45), cy - (r * 0.15))
        path_top.closeSubpath()

        grad_top = QLinearGradient(cx - r, cy - r, cx + r, cy)
        grad_top.setColorAt(0.0, QColor("#FFFFFF"))
        grad_top.setColorAt(0.6, QColor("#00F0FF"))
        grad_top.setColorAt(1.0, QColor("#0088CC"))
        painter.fillPath(path_top, QBrush(grad_top))

        # Lower overlapping diamond segment
        path_bottom = QPainterPath()
        path_bottom.moveTo(cx, cy + r)
        path_bottom.lineTo(cx - r, cy)
        path_bottom.lineTo(cx, cy - (r * 0.3))
        path_bottom.lineTo(cx + (r * 0.45), cy + (r * 0.15))
        path_bottom.closeSubpath()

        grad_bottom = QLinearGradient(cx + r, cy + r, cx - r, cy)
        grad_bottom.setColorAt(0.0, QColor("#00F0FF"))
        grad_bottom.setColorAt(0.7, QColor("#00B4D8"))
        grad_bottom.setColorAt(1.0, QColor("#0A2540"))
        painter.fillPath(path_bottom, QBrush(grad_bottom))


class LatencySliderWidget(QWidget):
    """
    Horizontal latency slider with integrated tick markers and min/max labels.
    """

    valueChanged = Signal(int)

    def __init__(self, min_val: int = 0, max_val: int = 1000, initial_val: int = 325, parent: QWidget = None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self._value = initial_val
        self._is_dragging = False

        self.setMinimumHeight(64)
        self.setCursor(Qt.PointingHandCursor)

    @property
    def value(self) -> int:
        return self._value

    def setValue(self, val: int):
        clamped = max(self.min_val, min(self.max_val, int(val)))
        if clamped != self._value:
            self._value = clamped
            self.update()
            self.valueChanged.emit(self._value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._update_from_mouse(event.position().x())

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self._update_from_mouse(event.position().x())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False

    def _update_from_mouse(self, mouse_x: float):
        track_pad = 20.0
        track_w = self.width() - (track_pad * 2.0)
        if track_w <= 0:
            return
        ratio = (mouse_x - track_pad) / track_w
        ratio = max(0.0, min(1.0, ratio))
        new_val = int(round(self.min_val + ratio * (self.max_val - self.min_val)))
        self.setValue(new_val)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = float(self.width())
        track_pad = 20.0
        track_y = 22.0
        track_h = 4.0
        track_w = w - (track_pad * 2.0)

        if track_w <= 0:
            return

        ratio = (self._value - self.min_val) / float(self.max_val - self.min_val)
        handle_x = track_pad + (ratio * track_w)

        # Base track
        base_track = QRectF(track_pad, track_y, track_w, track_h)
        base_path = QPainterPath()
        base_path.addRoundedRect(base_track, track_h / 2.0, track_h / 2.0)
        painter.fillPath(base_path, QBrush(QColor("#1A2030")))

        # Active track fill
        if ratio > 0.001:
            active_w = handle_x - track_pad
            active_track = QRectF(track_pad, track_y, active_w, track_h)
            active_path = QPainterPath()
            active_path.addRoundedRect(active_track, track_h / 2.0, track_h / 2.0)

            # Glow
            glow_pen = QPen(QColor(0, 240, 255, 90), 6.0, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(glow_pen)
            painter.drawLine(QPointF(track_pad, track_y + track_h / 2.0), QPointF(handle_x, track_y + track_h / 2.0))

            fill_grad = QLinearGradient(track_pad, 0, handle_x, 0)
            fill_grad.setColorAt(0.0, QColor("#00B4D8"))
            fill_grad.setColorAt(1.0, QColor("#00F0FF"))
            painter.fillPath(active_path, QBrush(fill_grad))

        # Tick Marks (11 ticks)
        num_ticks = 11
        for i in range(num_ticks):
            tx = track_pad + (i / (num_ticks - 1)) * track_w
            tick_top = track_y - 6.0
            tick_bottom = track_y + 10.0
            tick_color = QColor("#00C8E6") if tx <= handle_x else QColor("#2A334B")
            painter.setPen(QPen(tick_color, 1.2))
            painter.drawLine(QPointF(tx, tick_top), QPointF(tx, tick_bottom))

        # Handle with Glow
        glow_radius = 12.0
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 240, 255, 60)))
        painter.drawEllipse(QPointF(handle_x, track_y + track_h / 2.0), glow_radius, glow_radius)

        handle_radius = 8.0
        handle_grad = QLinearGradient(handle_x, track_y - handle_radius, handle_x, track_y + handle_radius)
        handle_grad.setColorAt(0.0, QColor("#55FFFF"))
        handle_grad.setColorAt(1.0, QColor("#00D2E0"))

        painter.setBrush(QBrush(handle_grad))
        painter.setPen(QPen(QColor("#FFFFFF"), 2.0))
        painter.drawEllipse(QPointF(handle_x, track_y + track_h / 2.0), handle_radius, handle_radius)

        # Labels
        font = QFont("Segoe UI", 8, QFont.Medium)
        painter.setFont(font)
        painter.setPen(QColor("#6B7280"))
        label_y = track_y + 20.0
        painter.drawText(QRectF(track_pad - 10, label_y, 50, 16), Qt.AlignLeft, f"{self.min_val}ms")
        painter.drawText(QRectF(w - track_pad - 50 + 10, label_y, 50, 16), Qt.AlignRight, f"{self.max_val}ms")


class SecondarySliderWidget(QWidget):
    """
    Compact secondary slider for Jitter and Packet Loss control.
    """

    valueChanged = Signal(float)

    def __init__(
        self,
        label: str,
        min_val: float = 0.0,
        max_val: float = 100.0,
        initial_val: float = 0.0,
        unit: str = "ms",
        accent_hex: str = "#00F0FF",
        parent: QWidget = None
    ):
        super().__init__(parent)
        self.label_text = label
        self.min_val = min_val
        self.max_val = max_val
        self._value = initial_val
        self.unit = unit
        self.accent_color = QColor(accent_hex)
        self._is_dragging = False

        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)

    @property
    def value(self) -> float:
        return self._value

    def setValue(self, val: float):
        clamped = max(self.min_val, min(self.max_val, float(val)))
        if abs(clamped - self._value) > 0.01:
            self._value = clamped
            self.update()
            self.valueChanged.emit(self._value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._update_from_mouse(event.position().x())

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self._update_from_mouse(event.position().x())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False

    def _update_from_mouse(self, mouse_x: float):
        track_pad = 12.0
        track_w = self.width() - (track_pad * 2.0)
        if track_w <= 0:
            return
        ratio = (mouse_x - track_pad) / track_w
        ratio = max(0.0, min(1.0, ratio))
        new_val = self.min_val + ratio * (self.max_val - self.min_val)
        self.setValue(new_val)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = float(self.width())
        track_pad = 12.0
        track_y = 30.0
        track_h = 3.5
        track_w = w - (track_pad * 2.0)

        # Header Text: Label and Value Readout
        font_lbl = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font_lbl)
        painter.setPen(QColor("#9CA3AF"))
        painter.drawText(QRectF(track_pad, 4, 120, 16), Qt.AlignLeft, self.label_text.upper())

        font_val = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font_val)
        painter.setPen(self.accent_color)
        val_str = f"±{int(self._value)}{self.unit}" if "±" in self.unit or self.label_text.lower() == "jitter" else f"{int(self._value)}{self.unit}"
        painter.drawText(QRectF(w - track_pad - 80, 4, 80, 16), Qt.AlignRight, val_str)

        if track_w <= 0:
            return

        ratio = (self._value - self.min_val) / float(self.max_val - self.min_val)
        handle_x = track_pad + (ratio * track_w)

        # Base track
        base_track = QRectF(track_pad, track_y, track_w, track_h)
        base_path = QPainterPath()
        base_path.addRoundedRect(base_track, track_h / 2.0, track_h / 2.0)
        painter.fillPath(base_path, QBrush(QColor("#1A2030")))

        # Active track fill
        if ratio > 0.001:
            active_w = handle_x - track_pad
            active_track = QRectF(track_pad, track_y, active_w, track_h)
            active_path = QPainterPath()
            active_path.addRoundedRect(active_track, track_h / 2.0, track_h / 2.0)
            painter.fillPath(active_path, QBrush(self.accent_color))

        # Handle
        handle_radius = 6.0
        painter.setBrush(QBrush(self.accent_color))
        painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        painter.drawEllipse(QPointF(handle_x, track_y + track_h / 2.0), handle_radius, handle_radius)


class StatusIndicatorWidget(QWidget):
    """
    Renders the 3 glowing emerald status dots with animation support.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFixedSize(36, 16)
        self._active = False
        self._pulse_alpha = 1.0

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def set_pulse_alpha(self, alpha: float):
        self._pulse_alpha = alpha
        if self._active:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        dots = [
            (6.0, 8.0, 3.0),
            (16.0, 8.0, 3.5),
            (27.0, 8.0, 4.5),
        ]

        for i, (cx, cy, r) in enumerate(dots):
            if self._active:
                if i == 2:
                    glow_a = int(90 * self._pulse_alpha)
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(QColor(16, 185, 129, glow_a)))
                    painter.drawEllipse(QPointF(cx, cy), r + 2.5, r + 2.5)

                    painter.setBrush(QBrush(QColor("#10B981")))
                else:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(QColor(16, 185, 129, 180)))
            else:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor("#374151")))

            painter.drawEllipse(QPointF(cx, cy), r, r)
