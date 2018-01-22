import typing

from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect, Qt, QSizeF
from PyQt5.QtGui import QPixmapCache

from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem
import openslide


class GraphicsTile(QGraphicsItem):
    def __init__(self, x_y_w_h, slide: openslide.OpenSlide, level, downsample):
        super().__init__()
        self.x_y_w_h = x_y_w_h
        self.slide_rect_0 = QRect(int(x_y_w_h[0] * downsample), int(self.x_y_w_h[1] * downsample), x_y_w_h[2],
                                  x_y_w_h[3])
        self.scene_rect = QRect(int(x_y_w_h[0] * downsample), int(self.x_y_w_h[1] * downsample), x_y_w_h[2] ,
                                x_y_w_h[3])
        # self.scene_rect = QRect(x_y_w_h[0], x_y_w_h[1], x_y_w_h[2], x_y_w_h[3])
        # self.scene_rect = QRect(0, 0, x_y_w_h[2], x_y_w_h[3])
        self.slide = slide
        self.level = level
        self.downsample = downsample
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)
        # self.setCacheMode(QGraphicsItem.ItemCoordinateCache, self.rect.size())
        self.cache_key = str(level) + str(self.slide_rect_0)
        # self.setFlag(QGraphicsItem.ItemClipsToShape, True)

    def pilimage_to_pixmap(self, pilimage):
        qim = ImageQt(pilimage)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix

    def boundingRect(self):
        # return QRectF(self.pos(), QSizeF(self.x_y_w_h[2], self.x_y_w_h[3]))
        # return QRectF(0, 0, self.x_y_w_h[2], self.x_y_w_h[3])
        # return QRectF(0, 0, self.x_y_w_h[2], self.x_y_w_h[3])
        return QRectF(0, 0, self.scene_rect.width(), self.scene_rect.height())
        # return QRectF(self.scene_rect)

    # def isVisible(self) -> bool:
    #     scene_contains = self.scene().sceneRect().contains(self.boundingRect())
    #     return scene_contains
    # return super().isVisible()

    # def isVisibleTo(self, parent: 'QGraphicsItem') -> bool:
    #     return super().isVisibleTo(parent)

    # def topLevelItem(self) -> 'QGraphicsItem':
    #     return 0

    # def shape(self):
    #     return QRectF(self.scene_rect)

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...):
        # print("pos ", self.pos())
        print("paint ", self.scene_rect, option.rect, option.exposedRect)
        self.pixmap = QPixmapCache.find(self.cache_key)
        if not self.pixmap:
            print("read", self.scene_rect)
            tile_pilimage = self.slide.read_region((self.slide_rect_0.x(), self.slide_rect_0.y()),
                                                   self.level, (self.slide_rect_0.width(), self.slide_rect_0.height()))
            self.pixmap = self.pilimage_to_pixmap(tile_pilimage)
            QPixmapCache.insert(self.cache_key, self.pixmap)

        # painter.drawPixmap(self.scene_rect, self.pixmap)
        painter.drawPixmap(self.boundingRect().toRect(), self.pixmap)
