import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect, Qt
from PyQt5.QtGui import QColor, QBrush

from PyQt5.QtWidgets import QGraphicsItem, QWidget

from elapsed_timer import elapsed_timer


class GraphicsGrid(QGraphicsItem):
    def __init__(self, grid_rects_0_level, colors, bounding_rect):
        super().__init__()
        self.grid_rects_0_level = grid_rects_0_level
        self.colors = colors
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(False)
        self.bounding_rect = bounding_rect
        # min_x = min(grid_rects_0_level, key=lambda x: x[0])[0]
        # min_y = min(grid_rects_0_level, key=lambda x: x[1])[1]
        # max_x_tuple = max(grid_rects_0_level, key=lambda x: x[0] + x[2])
        # max_x = max_x_tuple[0] + max_x_tuple[2]
        # max_y_tuple = max(grid_rects_0_level, key=lambda x: x[1] + x[3])
        # max_y = max_y_tuple[1] + max_y_tuple[3]
        # self.bounding_rect = (min_x, min_y, max_x - min_x, max_y - min_y)

        # self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.downsample = 1
        self.color_key__qrectfs_0_level = {}
        # self.color_key__qrectfs_0_level = {
        #     color.name(QColor.HexArgb): self.color_key__qrectfs_0_level.setdefault(color.name(QColor.HexArgb),
        #                                                                            []) + [QRectF(*grid_rect_0_level)]
        # for
        #     grid_rect_0_level, color in zip(grid_rects_0_level, colors)}
        # print(1)
        # pass

        # for grid_rect_0_level, color in zip(grid_rects_0_level, colors):
        #     color_key = color.name(QColor.HexArgb)
        #     self.color_key__qrectfs_0_level.setdefault(color_key, []).append(QRectF(*grid_rect_0_level))

        for grid_rect_0_level, color in zip(grid_rects_0_level, colors):
            self.color_key__qrectfs_0_level.setdefault(color, []).append(QRectF(*grid_rect_0_level))

    def update_downsmaple(self, downsample):
        self.downsample = downsample

    def boundingRect(self):
        return QRectF(self.bounding_rect[0], self.bounding_rect[1], self.bounding_rect[2] / self.downsample,
                      self.bounding_rect[3] / self.downsample)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...):
        painter.save()
        scale = 1 / self.downsample
        painter.scale(scale, scale)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        # for grid_rect, color in zip(self.grid_rects_0_level, self.colors):
        #     painter.setBrush(color)
        #     painter.drawRect(*grid_rect)
        for color_key in self.color_key__qrectfs_0_level:
            color = QColor(*color_key)
            painter.setBrush(color)
            painter.drawRects(self.color_key__qrectfs_0_level[color_key])
        painter.restore()
