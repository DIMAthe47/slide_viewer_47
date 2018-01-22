import typing

from PyQt5 import QtCore
from PyQt5.QtWidgets import QGraphicsScene


class MyGraphicsScene(QGraphicsScene):

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)

    # def items(self, rect: QtCore.QRectF, mode: QtCore.Qt.ItemSelectionMode = ..., order: QtCore.Qt.SortOrder = ...,
    #           deviceTransform: QtGui.QTransform = ...) -> typing.List[QGraphicsItem]:
    #     return super().items(rect, mode, order, deviceTransform)