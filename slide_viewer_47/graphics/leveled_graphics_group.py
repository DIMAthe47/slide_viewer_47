import typing

from PyQt5.QtCore import QRectF, Qt

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsItemGroup

from slide_viewer_47.graphics.my_graphics_group import MyGraphicsGroup


class LeveledGraphicsGroup(QGraphicsItemGroup):
    def __init__(self, levels: typing.List[int], parent=None):
        super().__init__(parent)
        self.levels = levels
        self.level__group = {}
        for level in levels:
            # group = QGraphicsItemGroup(self)
            group = MyGraphicsGroup(self)
            group.setVisible(False)
            self.level__group[level] = group
        self.visible_level = None
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(False)

        # self.setFlag(QGraphicsItem.ItemHasNoContents, True)
        # self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)
        # self.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)
        # self.setFlag(QGraphicsItem.ItemClipsToShape, True)

    def boundingRect(self):
        if self.visible_level:
            return self.level__group[self.visible_level].boundingRect()
        else:
            return QRectF()

    def add_item_to_level_group(self, level, item: QGraphicsItem):
        self.level__group[level].addToGroup(item)

    def remove_item_from_level_group(self, level, item: QGraphicsItem):
        self.level__group[level].removeFromGroup(item)

    def clear_level(self, level):
        group = self.level__group[level]
        for item in group.childItems():
            group.removeFromGroup(item)
            group.scene().removeItem(item)

    def update_visible_level(self, visible_level):
        self.visible_level = visible_level
        for level in self.levels:
            group = self.level__group[level]
            group.setVisible(level == visible_level)
