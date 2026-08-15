"""
LagForge - Obsidian Pill Toggle Switch (v1.101)
Capsule switch with glowing Active/Inactive states and animated pulsing neon.
"""

from PySide6.QtCore import Qt, Signal, QRectF, Property, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QBrush, QPen, QPainterPath
from PySide6.QtWidgets import QWidget


class PillSwitch(QWidget):
    """
    Pill-shaped toggle button with 'ACTIVE' (Emerald Glow) and 'INACTIVE' (Muted) states.
    Features pulsing glow animation when active.
    """

    toggled = Signal(bool)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._is_active = False
        self._pill_pos = 1.0
        self._pulse_val = 1.0
        self._pulse_direction = -1

        self.setFixedSize(160, 36)
        self.setCursor(Qt.PointingHandCursor)

        # Smooth slide animation
        self._anim = QPropertyAnimation(self, b"pill_pos", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        # Pulsing timer
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(40)  # 25 FPS pulse
        self._pulse_timer.timeout.connect(self._on_pulse_step)

    def get_pill_pos(self) -> float:
        return self._pill_pos

    def set_pill_pos(self, pos: float):
        self._pill_pos = pos
        self.update()

    pill_pos = Property(float, get_pill_pos, set_pill_pos)

    @property
    def is_active(self) -> bool:
        return self._is_active

    def _on_pulse_step(self):
        if not self._is_active:
            self._pulse_timer.stop()
            self._pulse_val = 1.0
            self.update()
            return

        self._pulse_val += self._pulse_direction * 0.04
        if self._pulse_val <= 0.4:
            self._pulse_val = 0.4
            self._pulse_direction = 1
        elif self._pulse_val >= 1.0:
            self._pulse_val = 1.0
            self._pulse_direction = -1

        self.update()

    def set_active(self, active: bool, animate: bool = True):
        if self._is_active == active:
            return
        self._is_active = active
        target = 0.0 if active else 1.0

        if active:
            self._pulse_direction = -1
            self._pulse_timer.start()
        else:
            self._pulse_timer.stop()
            self._pulse_val = 1.0

        if animate:
            self._anim.stop()
            self._anim.setStartValue(self._pill_pos)
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self._pill_pos = target
            self.update()

        self.toggled.emit(self._is_active)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_active(not self._is_active)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = float(self.width())
        h = float(self.height())
        radius = h / 2.0

        # Background Capsule
        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
        painter.fillPath(bg_path, QBrush(QColor("#13151E")))

        # Outer border
        border_pen = QPen(QColor("#212638"), 1.0)
        painter.setPen(border_pen)
        painter.drawPath(bg_path)

        # Sliding Pill Thumb
        thumb_pad = 3.0
        thumb_w = (w / 2.0) - thumb_pad
        thumb_h = h - (thumb_pad * 2.0)
        thumb_radius = thumb_h / 2.0

        x_left = thumb_pad
        x_right = (w / 2.0)
        thumb_x = x_left + (x_right - x_left) * self._pill_pos

        thumb_rect = QRectF(thumb_x, thumb_pad, thumb_w, thumb_h)
        thumb_path = QPainterPath()
        thumb_path.addRoundedRect(thumb_rect, thumb_radius, thumb_radius)

        if self._pill_pos < 0.5:
            # Active (Emerald Green with pulsing glow)
            glow_alpha = int(70 * self._pulse_val)
            glow_rect = thumb_rect.adjusted(-2, -2, 2, 2)
            glow_path = QPainterPath()
            glow_path.addRoundedRect(glow_rect, thumb_radius + 2, thumb_radius + 2)
            painter.fillPath(glow_path, QBrush(QColor(16, 185, 129, glow_alpha)))

            painter.fillPath(thumb_path, QBrush(QColor("#10B981")))
        else:
            painter.fillPath(thumb_path, QBrush(QColor("#212638")))

        # Labels
        font = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font)

        left_rect = QRectF(0, 0, w / 2.0, h)
        right_rect = QRectF(w / 2.0, 0, w / 2.0, h)

        if self._is_active:
            painter.setPen(QColor("#031F14"))
        else:
            painter.setPen(QColor("#4B5563"))
        painter.drawText(left_rect, Qt.AlignCenter, "ACTIVE")

        if not self._is_active:
            painter.setPen(QColor("#9CA3AF"))
        else:
            painter.setPen(QColor("#374151"))
        painter.drawText(right_rect, Qt.AlignCenter, "INACTIVE")
