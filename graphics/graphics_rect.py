import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect, Qt
from PyQt5.QtGui import QColor, QBrush

from PyQt5.QtWidgets import QWidget, QGraphicsRectItem


class GraphicsRect(QGraphicsRectItem):
    def __init__(self, x_y_w_h, color: QColor):
        super().__init__(*x_y_w_h)
        self.x_y_w_h = x_y_w_h
        self.color = color
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)
        self.brush = QBrush(self.color)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...):
        painter.save()
        painter.setBrush(self.brush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawRect(*self.x_y_w_h)
        painter.restore()
