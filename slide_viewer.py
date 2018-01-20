import PyQt5
import openslide
from PyQt5.QtCore import QPoint, Qt, QEvent, QRect, QSize, QRectF, QSizeF, pyqtSignal, QPointF, QMarginsF
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QColor, QImage, QPainter, QTransform
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel, QRubberBand

from graphics.slide_graphics_group import SlideGraphicsGroup
from utils import point_to_str, SlideHelper


def build_screenshot_image(scene: QGraphicsScene, scene_rect: QRectF, image_size: QSize) -> QImage:
    # pixmap = self.view.viewport().grab()
    # pixmap.save("view_screenshot.png")
    image = QImage(image_size, QImage.Format_RGBA8888)
    painter = QPainter(image)
    image.fill(painter.background().color())
    scene.render(painter, QRectF(image.rect()), scene_rect)
    painter.end()
    return image


class SlideViewer(QWidget):
    eventSignal = pyqtSignal(PyQt5.QtCore.QEvent)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.init_view()
        self.init_labels()
        self.init_layout()

    def init_view(self):
        self.scene = QGraphicsScene()
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.viewport().installEventFilter(self)

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.mouse_press_view = QPoint()

    def init_labels(self):
        self.level_label = QLabel()
        self.level_label.setWordWrap(True)
        self.selected_rect_label = QLabel()
        self.selected_rect_label.setWordWrap(True)
        self.mouse_pos_scene_label = QLabel()
        self.mouse_pos_scene_label.setWordWrap(True)

    def init_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(self.level_label)
        layout.addWidget(self.mouse_pos_scene_label)
        layout.addWidget(self.selected_rect_label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def load_slide(self, slide_path, preffered_rects_count=2000, zoom_step=1.15):
        self.zoom_step = zoom_step
        self.slide_path = slide_path
        self.slide = openslide.OpenSlide(slide_path)
        self.slide_helper = SlideHelper(self.slide)

        self.selected_rect_0_level = None

        self.slide_graphics = SlideGraphicsGroup(self.slide_path, preffered_rects_count)
        self.scene.clear()
        self.scene.addItem(self.slide_graphics)

        max_level = self.slide_helper.get_max_level()
        self.logical_zoom = 1 / self.slide_helper.get_downsample_for_level(max_level)

        self.physical_zoom = 1
        self.current_level = self.slide_helper.get_max_level()

        self.fit_in_view()

        self.update_labels()

    def fit_in_view(self):
        current_level = self.get_level_for_logical_zoom(self.logical_zoom)
        self.slide_graphics.update_visible_level(current_level)
        self.update_scene_rect_for_level(current_level)
        margins = QMarginsF(200, 200, 200, 200)
        self.view.fitInView(self.scene.sceneRect() + margins, Qt.KeepAspectRatio)
        scale_ = self.view.transform().m11()
        self.logical_zoom *= scale_

        self.current_level = self.slide_helper.get_max_level()
        self.physical_zoom *= scale_

    def eventFilter(self, qobj: 'QObject', event: 'QEvent'):
        self.eventSignal.emit(event)
        if isinstance(event, QWheelEvent):
            self.process_viewport_wheel_event(event)
            # we handle wheel event to prevent GraphicsView interpret it as scrolling
            return True
        elif isinstance(event, QMouseEvent):
            if event.button() == Qt.MiddleButton:
                self.take_screenshot()
            elif event.button() == Qt.LeftButton:
                if event.type() == QEvent.MouseButtonPress:
                    self.mouse_press_view = QPoint(event.pos())
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, QSize()))
                    self.rubber_band.show()
                    return True
                elif event.type() == QEvent.MouseButtonRelease:
                    self.rubber_band.hide()
                    self.remember_selected_rect_params()
                    self.slide_graphics.update_selected_rect_0_level(self.selected_rect_0_level)
                    self.update_labels()
                    self.scene.invalidate()
                    return True
            elif event.type() == QEvent.MouseMove:
                self.mouse_pos_scene_label.setText(
                    "mouse pos scene: " + point_to_str(self.view.mapToScene(event.pos())))
                if not self.mouse_press_view.isNull():
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, event.pos()).normalized())
                return True

        return False

    def take_screenshot(self):
        scene_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        image = build_screenshot_image(self.scene, scene_rect, self.view.viewport().size())
        image.save("view_screenshot_image.png")

    def remember_selected_rect_params(self):
        pos_scene = self.view.mapToScene(self.rubber_band.pos() - self.view.pos())
        rect_scene = self.view.mapToScene(self.rubber_band.rect()).boundingRect()
        downsample = self.get_current_level_downsample()
        selected_qrectf_0_level = QRectF(pos_scene * downsample,
                                         QSizeF(rect_scene.size() * downsample))
        self.selected_rect_0_level = selected_qrectf_0_level.getRect()

    def process_viewport_wheel_event(self, event: QWheelEvent):
        zoom_in = self.zoom_step
        zoom_out = 1 / zoom_in
        zoom_ = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.update_scale(event.pos(), zoom_)
        event.accept()

    def set_view_from_rect(self, rect_scene, visible_level):
        # another way to adjust view - but scaling and translating will be not accurate
        self.view.fitInView(rect_scene, Qt.KeepAspectRatio)
        self.update_items_visibility_for_current_level()

    def update_scale(self, mouse_pos: QPoint, zoom):
        old_mouse_pos_scene = self.view.mapToScene(mouse_pos)
        old_view_scene_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()

        # old_level_downsample = self.get_current_level_downsample()
        # self.logical_zoom *= zoom
        old_level = self.get_best_level_for_zoom(self.view.transform().m11())
        old_level_downsample = self.slide_helper.get_downsample_for_level(old_level)
        new_level = self.get_best_level_for_zoom(self.view.transform().m11() * zoom)
        # new_level_downsample = self.get_current_level_downsample()
        new_level_downsample = self.slide_helper.get_downsample_for_level(new_level)

        level_scale_delta = 1 / (new_level_downsample / old_level_downsample)

        r = old_view_scene_rect.topLeft()
        m = old_mouse_pos_scene
        new_view_scene_rect_top_left = (m - (m - r) / zoom) * level_scale_delta
        new_view_scene_rect = QRectF(new_view_scene_rect_top_left,
                                     old_view_scene_rect.size() * level_scale_delta / zoom)

        # current_level = self.get_level_for_logical_zoom(self.logical_zoom)
        # self.update_scene_rect_for_level(current_level)
        self.update_scene_rect_for_level(new_level)

        scale_ = self.view.transform().m11() * zoom * new_level_downsample / old_level_downsample
        transform = QTransform().scale(scale_, scale_).translate(-new_view_scene_rect.x(),
                                                                 -new_view_scene_rect.y())
        self.reset_view_transform()
        self.view.setTransform(transform, False)
        # self.update_items_visibility_for_current_level()
        self.slide_graphics.update_visible_level(new_level)
        self.update_labels()
        # self.get_best_level_for_zoom()

    def get_best_level_for_zoom(self, zoom):
        scene_width = self.scene.sceneRect().size().width()
        candidates = [0]
        for level in self.slide_helper.get_levels():
            w, h = self.slide.level_dimensions[level]
            if scene_width * zoom  < w:
                candidates.append(level)
        best_level = max(candidates)
        print(best_level)
        return best_level

    def update_from_rect_and_downsample(self, rect, downsample):
        self.update_scene_rect_for_level()
        if rect:
            self.view.translate(rect.x(), rect.y())

    def update_scene_rect_for_level(self, level):
        rect = self.slide_helper.get_rect_for_level(level)
        # rect = QRectF(0, 0, 100000, 100000)
        self.scene.setSceneRect(rect)

    def update_items_visibility_for_current_level(self):
        current_level = self.get_level_for_logical_zoom(self.logical_zoom)
        self.slide_graphics.update_visible_level(current_level)

    def update_labels(self):
        current_level = self.get_best_level_for_zoom(self.view.transform().m11())
        # current_level = self.get_level_for_logical_zoom(self.logical_zoom)
        level_downsample = self.slide.level_downsamples[current_level]
        level_size = self.slide_helper.get_level_size_for_level(current_level)
        self.level_label.setText(
            "current level, downsample, size: {}, {:.4f}, ({}, {})".format(current_level, level_downsample,
                                                                           *level_size))
        if self.selected_rect_0_level:
            self.selected_rect_label.setText(
                "selected rect (0-level): ({:.2f},{:.2f})".format(*self.selected_rect_0_level))

    def reset_view_transform(self):
        # print("view_pos before resetTransform:", self.view_pos_scene_str())
        # print("dx before resetTransform:", self.view.transform().dx())
        # print("horizontalScrollBar before resetTransform:", self.view.horizontalScrollBar().value())
        self.view.resetTransform()
        self.view.horizontalScrollBar().setValue(0)
        self.view.verticalScrollBar().setValue(0)
        # print("view_pos after resetTransform:", self.view_pos_scene_str())
        # print("dx after resetTransform:", self.view.transform().dx())
        # print("horizontalScrollBar after resetTransform:", self.view.horizontalScrollBar().value())

    def get_level_for_logical_zoom(self, logical_zoom):
        return self.current_level
        return self.slide_helper.get_best_level_for_downsample(1 / logical_zoom)

    def get_current_level_downsample(self):
        return self.slide_helper.get_downsample_for_level(self.current_level)
        current_level = self.get_level_for_logical_zoom(self.logical_zoom)
        level_downsample = self.slide_helper.get_downsample_for_level(current_level)
        return level_downsample

    def get_current_view_scene_rect(self):
        return self.view.mapToScene(self.view.rect()).boundingRect()
