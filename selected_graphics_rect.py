import typing
from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect, Qt
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
        painter.drawRect(self.qrectf)
