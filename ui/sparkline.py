"""
LagForge - Dynamic Sparkline Widget
Real-time high-performance network activity sparkline using QPainter.
"""

from collections import deque
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QPainterPath,
    QLinearGradient,
    QBrush,
)
from PySide6.QtWidgets import QWidget


class SparklineWidget(QWidget):
    """
    Renders a live, glowing sparkline graph representing network throughput / delayed packets.
    """

    def __init__(self, max_points: int = 60, parent: QWidget = None):
        super().__init__(parent)
        self.max_points = max_points
        self.data_points = deque([0.0] * max_points, maxlen=max_points)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setMinimumHeight(64)

        # Style colors
        self.line_color = QColor("#00F0FF")
        self.glow_color = QColor(0, 240, 255, 60)
        self.fill_top_color = QColor(0, 240, 255, 45)
        self.fill_bottom_color = QColor(0, 240, 255, 0)

    def add_data_point(self, value: float):
        """Appends a new reading to the rolling sparkline window."""
        self.data_points.append(max(0.0, float(value)))
        self.update()

    def reset(self):
        """Clears current graph data."""
        self.data_points = deque([0.0] * self.max_points, maxlen=self.max_points)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        width = self.width()
        height = self.height()

        if width <= 0 or height <= 0:
            return

        points = list(self.data_points)
        n = len(points)
        if n < 2:
            return

        # Scale data
        max_val = max(points)
        if max_val < 10.0:
            max_val = 20.0  # minimum baseline for clean visual headroom

        # Vertical padding
        top_pad = 8.0
        bottom_pad = 6.0
        usable_height = height - top_pad - bottom_pad

        # Compute point coordinates
        step_x = width / (n - 1)
        coords = []
        for i, val in enumerate(points):
            x = i * step_x
            normalized_y = (val / max_val)
            # Invert Y for screen coordinates
            y = height - bottom_pad - (normalized_y * usable_height)
            coords.append(QPointF(x, y))

        # Build path with smooth polyline / cubic curves
        path = QPainterPath()
        path.moveTo(coords[0])
        for i in range(1, len(coords)):
            # Midpoint smoothing
            p0 = coords[i - 1]
            p1 = coords[i]
            c1 = QPointF((p0.x() + p1.x()) / 2.0, p0.y())
            c2 = QPointF((p0.x() + p1.x()) / 2.0, p1.y())
            path.cubicTo(c1, c2, p1)

        # Draw filled gradient underneath the line
        fill_path = QPainterPath(path)
        fill_path.lineTo(width, height)
        fill_path.lineTo(0, height)
        fill_path.closeSubpath()

        gradient = QLinearGradient(0, top_pad, 0, height)
        gradient.setColorAt(0.0, self.fill_top_color)
        gradient.setColorAt(1.0, self.fill_bottom_color)

        painter.fillPath(fill_path, QBrush(gradient))

        # Draw outer neon glow pass
        glow_pen = QPen(self.glow_color, 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(glow_pen)
        painter.drawPath(path)

        # Draw crisp foreground curve
        main_pen = QPen(self.line_color, 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(main_pen)
        painter.drawPath(path)
