import typing

from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect, Qt
from PyQt5.QtGui import QPixmapCache, QColor, QBrush

from PyQt5.QtWidgets import QGraphicsItem, QWidget, QGraphicsRectItem, QGraphicsItemGroup
import openslide


class LeveledGraphicsGroup(QGraphicsItemGroup):
    def __init__(self, levels: typing.List[int]):
        super().__init__()
        self.levels = levels
        self.level__group = {}
        for level in levels:
            group = QGraphicsItemGroup(self)
            group.setVisible(False)
            self.level__group[level] = group
        self.visible_level = None
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(False)

    def boundingRect(self):
        bounding_rect = QRectF()
        if self.visible_level:
            return self.level__group[self.visible_level].boundingRect()
        return bounding_rect

    def add_item_to_level_group(self, level, item: QGraphicsItem):
        self.level__group[level].addToGroup(item)
        # item.setVisible(False)

    def remove_item_from_level_group(self, level, item: QGraphicsItem):
        self.level__group[level].removeFromGroup(item)

    def clear_level(self, level):
        group = self.level__group[level]
        for item in group.childItems():
            group.removeFromGroup(item)

    def update_visible_level(self, visible_level):
        self.visible_level = visible_level
        for level in self.levels:
            group = self.level__group[level]
            group.setVisible(level == visible_level)
