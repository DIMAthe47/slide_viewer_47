import typing

from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem


class MyGraphicsGroup(QGraphicsItemGroup):

    def __init__(self, parent: typing.Optional['QGraphicsItem'] = None) -> None:
        super().__init__(parent)
        # self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)
        # self.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)
        # self.setFlag(QGraphicsItem.ItemClipsToShape, True)
        # self.setFlag(QGraphicsItem.ItemHasNoContents, True)

    def __str__(self) -> str:
        return "{}: children count: {}".format(self.__class__.__name__, len(self.childItems()))

    def __repr__(self) -> str:
        return self.__str__()

    # def boundingRect(self) -> QRectF:
    #     return QRectF()
