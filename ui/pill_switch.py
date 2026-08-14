"""
LagForge - Obsidian Pill Toggle Switch
Capsule switch with glowing Active/Inactive states.
"""

from PySide6.QtCore import Qt, Signal, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QFont, QBrush, QPen, QPainterPath
from PySide6.QtWidgets import QWidget


class PillSwitch(QWidget):
    """
    Pill-shaped toggle button with 'ACTIVE' (Emerald Glow) and 'INACTIVE' (Muted) states.
    """

    toggled = Signal(bool)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._is_active = False
        self._pill_pos = 1.0  # 0.0 for ACTIVE (left), 1.0 for INACTIVE (right)

        self.setFixedSize(160, 36)
        self.setCursor(Qt.PointingHandCursor)

        # Smooth slide animation
        self._anim = QPropertyAnimation(self, b"pill_pos", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_pill_pos(self) -> float:
        return self._pill_pos

    def set_pill_pos(self, pos: float):
        self._pill_pos = pos
        self.update()

    pill_pos = Property(float, get_pill_pos, set_pill_pos)

    @property
    def is_active(self) -> bool:
        return self._is_active

    def set_active(self, active: bool, animate: bool = True):
        if self._is_active == active:
            return
        self._is_active = active
        target = 0.0 if active else 1.0

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

        # Calculate thumb X position based on interpolation
        x_left = thumb_pad
        x_right = (w / 2.0)
        thumb_x = x_left + (x_right - x_left) * self._pill_pos

        thumb_rect = QRectF(thumb_x, thumb_pad, thumb_w, thumb_h)
        thumb_path = QPainterPath()
        thumb_path.addRoundedRect(thumb_rect, thumb_radius, thumb_radius)

        if self._pill_pos < 0.5:
            # Active (Emerald Green glow)
            # Outer glow
            glow_rect = thumb_rect.adjusted(-2, -2, 2, 2)
            glow_path = QPainterPath()
            glow_path.addRoundedRect(glow_rect, thumb_radius + 2, thumb_radius + 2)
            painter.fillPath(glow_path, QBrush(QColor(16, 185, 129, 60)))

            # Pill body
            painter.fillPath(thumb_path, QBrush(QColor("#10B981")))
        else:
            # Inactive (Muted Slate highlight)
            painter.fillPath(thumb_path, QBrush(QColor("#212638")))

        # Draw Text Labels
        font = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font)

        left_rect = QRectF(0, 0, w / 2.0, h)
        right_rect = QRectF(w / 2.0, 0, w / 2.0, h)

        # "ACTIVE" text color
        if self._is_active:
            painter.setPen(QColor("#031F14"))  # Dark contrast against bright emerald
        else:
            painter.setPen(QColor("#4B5563"))  # Muted

        painter.drawText(left_rect, Qt.AlignCenter, "ACTIVE")

        # "INACTIVE" text color
        if not self._is_active:
            painter.setPen(QColor("#9CA3AF"))  # Crisp Cool Gray
        else:
            painter.setPen(QColor("#374151"))  # Muted

        painter.drawText(right_rect, Qt.AlignCenter, "INACTIVE")
