import random

import PyQt5
import openslide
from PyQt5.QtCore import QPoint, Qt, QEvent, QRect, QSize, QRectF, QSizeF, pyqtSignal
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QColor, QImage, QPainter
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel, QRubberBand, \
    QGraphicsItemGroup, QHBoxLayout

from graphics.leveled_graphics_group import LeveledGraphicsGroup
from graphics.slide_graphics_group import SlideGraphicsGroup
from graphics_grid import GraphicsGrid
from graphics_rect import GraphicsRect
from graphics_tile import GraphicsTile
from selected_graphics_rect import SelectedGraphicsRect
from utils import slice_rect, rect_to_str, point_to_str, SlideHelper


class SlideViewer(QWidget):
    eventSignal = pyqtSignal(PyQt5.QtCore.QEvent)

    # @staticmethod
    # def screenshot(cls, slide_path, screenshot_size ,rect_0_level, grid_show):

    def __init__(self, parent: QWidget = None, zoom_step=1.15):
        super().__init__(parent)
        if parent and parent.layout():
            parent.layout().setContentsMargins(0, 0, 0, 0)
        self.zoom_step = zoom_step
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.level_label = QLabel()
        self.level_label.setWordWrap(True)
        self.selected_rect_label = QLabel()
        self.selected_rect_label.setWordWrap(True)
        self.mouse_pos_scene_label = QLabel()
        self.mouse_pos_scene_label.setWordWrap(True)
        # layout.addWidget(self.level_label)
        # layout.addWidget(self.mouse_pos_scene_label)
        # layout.addWidget(self.selected_rect_label)

        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.viewport().installEventFilter(self)
        # self.view.items().clear()
        # self.view.invalidateScene()

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.mouse_press_view = QPoint()

    def load_slide(self, slide_path, preffered_rects_count=2000):
        self.slide_path = slide_path
        self.slide = openslide.OpenSlide(slide_path)
        self.slide_helper = SlideHelper(self.slide)

        self.slide_graphics = SlideGraphicsGroup(self.slide_path, preffered_rects_count)
        self.scene.clear()
        self.scene.addItem(self.slide_graphics)

        self.init_scale()

    def init_scale(self):
        self.reset_transform()
        slide_rect_size = self.slide_helper.get_rect_for_level(self.slide_helper.get_max_level()).size()
        # ratio = 1.25
        ratio = 1
        view_width = self.view.viewport().width()
        view_height = self.view.viewport().height()
        zoom_width = view_width / (ratio * slide_rect_size.width())
        zoom_height = view_height / (ratio * slide_rect_size.height())
        zoom_ = min([zoom_width, zoom_height])
        self.logical_zoom = 1 / self.slide_helper.get_downsample_for_level(self.slide_helper.get_max_level())
        self.zoom_for_current_level = 1
        self.update_scale(QPoint(0, 0), zoom_)

    def update_from_rect_and_downsample(self, rect, downsample):
        self.update_scene_rect_for_current_level()
        if rect:
            self.view.translate(rect.x(), rect.y())

    def eventFilter(self, qobj: 'QObject', event: 'QEvent'):
        self.eventSignal.emit(event)
        if isinstance(event, QWheelEvent):
            self.process_viewport_wheel_event(event)
            # we handle wheel event to prevent GraphicsView interpret it as scrolling
            return True
        elif isinstance(event, QMouseEvent):
            if event.button() == Qt.MiddleButton:
                # pixmap = self.view.viewport().grab()
                # pixmap.save("view_screenshot.png")
                image = QImage(QSize(self.view.viewport().size()), QImage.Format_RGBA8888)
                painter = QPainter(image)
                # painter.begin()
                scene_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
                self.scene.render(painter, QRectF(image.rect()), scene_rect)
                painter.end()
                image.save("view_screenshot_image.png")

            elif event.button() == Qt.LeftButton:
                if event.type() == QEvent.MouseButtonPress:
                    self.mouse_press_view = QPoint(event.pos())
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, QSize()))
                    self.rubber_band.show()
                    return True
                if event.type() == QEvent.MouseButtonRelease:
                    self.rubber_band.hide()
                    self.remember_selected_rect_params()
                    self.update_selected_rect_view()
                    return True
            elif event.type() == QEvent.MouseMove:
                self.mouse_pos_scene_label.setText(
                    "mouse pos scene: " + point_to_str(self.view.mapToScene(event.pos())))
                if not self.mouse_press_view.isNull():
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, event.pos()).normalized())
                return True

        return False

    def remember_selected_rect_params(self):
        pos_scene = self.view.mapToScene(self.rubber_band.pos() - self.view.pos())
        rect_scene = self.view.mapToScene(self.rubber_band.rect()).boundingRect()
        downsample = self.get_current_level_downsample()
        selected_qrectf_0_level = QRectF(pos_scene * downsample,
                                         QSizeF(rect_scene.size() * downsample))
        self.selected_rect_0_level = selected_qrectf_0_level.getRect()

    def update_selected_rect_view(self):
        self.selected_rect_label.setText("selected rect (0-level): {}".format(self.selected_rect_0_level))
        self.slide_graphics.update_selected_rect_0_level(self.selected_rect_0_level)

    def process_viewport_wheel_event(self, event: QWheelEvent):
        zoom_in = self.zoom_step
        zoom_out = 1 / zoom_in
        zoom_ = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.update_scale(event.pos(), zoom_)
        event.accept()

    def update_scale(self, mouse_pos: QPoint, zoom):
        old_mouse_pos_scene = self.view.mapToScene(mouse_pos)
        old_level_downsample = self.get_current_level_downsample()

        self.logical_zoom *= zoom
        self.view.scale(zoom, zoom)
        self.zoom_for_current_level *= zoom

        new_level_downsample = self.get_current_level_downsample()
        if old_level_downsample == new_level_downsample:
            self.update_scene_rect_for_current_level()

        new_mouse_pos_scene = self.view.mapToScene(mouse_pos)
        mouse_pos_delta = new_mouse_pos_scene - old_mouse_pos_scene
        self.view.translate(mouse_pos_delta.x(), mouse_pos_delta.y())

        if old_level_downsample != new_level_downsample:
            new_view_pos_scene = self.view.mapToScene(self.view.rect().topLeft())
            level_scale_delta = 1 / (new_level_downsample / old_level_downsample)
            shift_scene = new_view_pos_scene
            shift_scene *= level_scale_delta
            self.reset_transform()
            self.update_scene_rect_for_current_level()
            scale_ = self.zoom_for_current_level * new_level_downsample / old_level_downsample
            # scale_ comes from equation (size*zoom/downsample) == (new_size*new_zoom/new_downsample)
            self.view.scale(scale_, scale_)
            self.view.translate(-shift_scene.x(), -shift_scene.y())
            self.zoom_for_current_level = scale_

        self.update_items_visibility_for_current_level()
        self.update_current_view_params_level()

    def get_current_level(self):
        return self.slide.get_best_level_for_downsample(1 / self.logical_zoom)

    def get_current_level_downsample(self):
        best_level = self.get_current_level()
        level_downsample = self.slide.level_downsamples[best_level]
        return level_downsample

    def get_current_view_scene_rect(self):
        return self.view.mapToScene(self.view.rect()).boundingRect()

    def update_scene_rect_for_current_level(self):
        best_level = self.get_current_level()
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(best_level))

    def update_items_visibility_for_current_level(self):
        best_level = self.get_current_level()
        self.slide_graphics.update_visible_level(best_level)

    def update_current_view_params_level(self):
        best_level = self.get_current_level()
        level_downsample = self.slide.level_downsamples[best_level]
        level_size = self.slide_helper.get_level_size_for_level(best_level)
        self.level_label.setText(
            "current level, downsample, size: {}, {:.4f}, ({}, {})".format(best_level, level_downsample, *level_size))

    def reset_transform(self):
        # print("view_pos before resetTransform:", self.view_pos_scene_str())
        # print("dx before resetTransform:", self.view.transform().dx())
        # print("horizontalScrollBar before resetTransform:", self.view.horizontalScrollBar().value())
        self.view.resetTransform()
        self.view.horizontalScrollBar().setValue(0)
        self.view.verticalScrollBar().setValue(0)
        # print("view_pos after resetTransform:", self.view_pos_scene_str())
        # print("dx after resetTransform:", self.view.transform().dx())
        # print("horizontalScrollBar after resetTransform:", self.view.horizontalScrollBar().value())
