"""
LagForge - Custom UI Controls
Custom widgets for Slider with Ticks, Geometric Logo, and Status Indicator.
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
from PySide6.QtWidgets import QWidget, QSlider


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

        self.setMinimumHeight(70)
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
        track_pad = 24.0
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
        h = float(self.height())

        track_pad = 24.0
        track_y = 26.0
        track_h = 4.0
        track_w = w - (track_pad * 2.0)

        if track_w <= 0:
            return

        ratio = (self._value - self.min_val) / float(self.max_val - self.min_val)
        handle_x = track_pad + (ratio * track_w)

        # 1. Base track (Dark Slate)
        base_track = QRectF(track_pad, track_y, track_w, track_h)
        base_path = QPainterPath()
        base_path.addRoundedRect(base_track, track_h / 2.0, track_h / 2.0)
        painter.fillPath(base_path, QBrush(QColor("#1A2030")))

        # 2. Active fill track (Cyan Gradient with slight glow)
        if ratio > 0.001:
            active_w = handle_x - track_pad
            active_track = QRectF(track_pad, track_y, active_w, track_h)
            active_path = QPainterPath()
            active_path.addRoundedRect(active_track, track_h / 2.0, track_h / 2.0)

            # Active glow
            glow_pen = QPen(QColor(0, 240, 255, 100), 8.0, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(glow_pen)
            painter.drawLine(QPointF(track_pad, track_y + track_h / 2.0), QPointF(handle_x, track_y + track_h / 2.0))

            # Active line
            fill_grad = QLinearGradient(track_pad, 0, handle_x, 0)
            fill_grad.setColorAt(0.0, QColor("#00B4D8"))
            fill_grad.setColorAt(1.0, QColor("#00F0FF"))
            painter.fillPath(active_path, QBrush(fill_grad))

        # 3. Tick Marks (11 ticks for 0ms, 100ms, ..., 1000ms)
        num_ticks = 11
        for i in range(num_ticks):
            tx = track_pad + (i / (num_ticks - 1)) * track_w
            tick_top = track_y - 7.0
            tick_bottom = track_y + 11.0

            # Tick line
            if tx <= handle_x:
                tick_color = QColor("#00C8E6")
            else:
                tick_color = QColor("#2A334B")

            painter.setPen(QPen(tick_color, 1.5))
            painter.drawLine(QPointF(tx, tick_top), QPointF(tx, tick_bottom))

        # 4. Handle (Electric Cyan with Glow & White Core)
        # Outer glow
        glow_radius = 14.0
        glow_grad = QLinearGradient(handle_x - glow_radius, track_y, handle_x + glow_radius, track_y)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 240, 255, 70)))
        painter.drawEllipse(QPointF(handle_x, track_y + track_h / 2.0), glow_radius, glow_radius)

        # Handle Circle Body
        handle_radius = 9.0
        handle_grad = QLinearGradient(handle_x, track_y - handle_radius, handle_x, track_y + handle_radius)
        handle_grad.setColorAt(0.0, QColor("#55FFFF"))
        handle_grad.setColorAt(1.0, QColor("#00D2E0"))

        painter.setBrush(QBrush(handle_grad))
        painter.setPen(QPen(QColor("#FFFFFF"), 2.0))
        painter.drawEllipse(QPointF(handle_x, track_y + track_h / 2.0), handle_radius, handle_radius)

        # 5. Min / Max Text Labels
        font = QFont("Segoe UI", 9, QFont.Medium)
        painter.setFont(font)
        painter.setPen(QColor("#6B7280"))

        label_y = track_y + 24.0
        painter.drawText(QRectF(track_pad - 10, label_y, 60, 20), Qt.AlignLeft, f"{self.min_val}ms")
        painter.drawText(QRectF(w - track_pad - 60 + 10, label_y, 60, 20), Qt.AlignRight, f"{self.max_val}ms")


class StatusIndicatorWidget(QWidget):
    """
    Renders the 3 glowing emerald status dots.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFixedSize(36, 16)
        self._active = False

    def set_active(self, active: bool):
        self._active = active
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
                    # Pulsing / Glowing main dot
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(QColor(16, 185, 129, 90)))
                    painter.drawEllipse(QPointF(cx, cy), r + 2.5, r + 2.5)

                    painter.setBrush(QBrush(QColor("#10B981")))
                else:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(QColor(16, 185, 129, 180)))
            else:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor("#374151")))

            painter.drawEllipse(QPointF(cx, cy), r, r)
