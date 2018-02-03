from PyQt5.QtCore import QSize, QRectF, Qt, QSizeF, QPointF, QRect, QPoint
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItemGroup, QGraphicsView



def paint_screenshot_image(painter: QPainter, scene: QGraphicsScene, image_size: QSize, scene_rect: QRectF = QRectF(),
                           transparent_background=False) -> QImage:
    # with elapsed_timer() as elapsed:
    painter.fillRect(QRect(QPoint(0, 0), image_size), painter.background().color())
    scene_items = scene.items(scene_rect, Qt.IntersectsItemBoundingRect)
    only_leaf_items = [item for item in scene_items if len(item.childItems()) == 0]
    item_parents = {}
    item_groups = {}
    for item in only_leaf_items:
        if item.group():
            item_groups[item] = item.group()
            item.group().setVisible(False)
        elif item.parentItem():
            item_parents[item] = item.parentItem()
            item.parentItem().setVisible(False)
    group_for_screenshot = QGraphicsItemGroup()
    for item in only_leaf_items:
        group_for_screenshot.addToGroup(item)
    scene.addItem(group_for_screenshot)
    group_for_screenshot.setVisible(True)
    # scene_items2 = scene.items(scene_rect, Qt.IntersectsItemBoundingRect)
    # print(scene_items2)
    # print("before render==========================================")
    rendered_size = scene_rect.size().scaled(QSizeF(image_size), Qt.KeepAspectRatio)
    dsize = QSizeF(image_size) - rendered_size
    top_left = QPointF(dsize.width() / 2, dsize.height() / 2)
    scene.render(painter, QRectF(top_left, rendered_size), scene_rect, Qt.KeepAspectRatio)
    scene.destroyItemGroup(group_for_screenshot)

    for item in item_parents:
        parent = item_parents[item]
        item.setParentItem(parent)
        parent.setVisible(True)
    for item in item_groups:
        group = item_groups[item]
        group.addToGroup(item)
        group.setVisible(True)

    # print("paint_screenshot_image", elapsed())


def build_screenshot_image(scene: QGraphicsScene, image_size: QSize, scene_rect: QRectF = QRectF()) -> QImage:
    image = QImage(image_size, QImage.Format_RGBA8888)
    painter = QPainter(image)
    paint_screenshot_image(painter, scene, image_size, scene_rect)
    painter.end()
    return image


def build_screenshot_image_from_view(view: QGraphicsView, image_size: QSize) -> QImage:
    image = QImage(image_size, QImage.Format_RGBA8888)
    painter = QPainter(image)
    pixmap = view.viewport().grab()
    painter.drawPixmap(image.rect(), pixmap)
    painter.end()
    return image
