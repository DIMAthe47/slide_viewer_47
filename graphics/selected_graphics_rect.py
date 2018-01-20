import typing
from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect, Qt
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsItem, QWidget


class SelectedGraphicsRect(QGraphicsItem):
    def __init__(self, qrectf: QRectF):
        super().__init__()
        self.qrectf = QRectF(qrectf)
        self.setAcceptedMouseButtons(Qt.NoButton)

    def boundingRect(self):
        return self.qrectf

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...):
        painter.save()
        pen = QPen(QColor(0, 0, 0, 255))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawRect(self.qrectf)
        painter.restore()
