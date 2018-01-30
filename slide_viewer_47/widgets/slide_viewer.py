from PyQt5 import QtCore

import PyQt5
from PyQt5.QtCore import QPoint, Qt, QEvent, QRect, QSize, QRectF, pyqtSignal, QMarginsF
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QTransform, QPaintEvent, QShowEvent
from PyQt5.QtWidgets import QWidget, QGraphicsView, QVBoxLayout, QLabel, QRubberBand, QMessageBox, QHBoxLayout, QFrame, \
    QGroupBox

from slide_viewer_47.common.screenshot_builders import build_screenshot_image
from slide_viewer_47.common.slide_view_params import SlideViewParams
from slide_viewer_47.graphics.my_graphics_scene import MyGraphicsScene
from slide_viewer_47.graphics.slide_graphics_group import SlideGraphicsGroup
from slide_viewer_47.common.utils import point_to_str
from slide_viewer_47.common.slide_helper import SlideHelper


class SlideViewer(QWidget):
    eventSignal = pyqtSignal(PyQt5.QtCore.QEvent)

    def __init__(self, parent: QWidget = None, viewer_top_else_left=True):
        super().__init__(parent)
        self.init_view()
        self.init_labels(word_wrap=viewer_top_else_left)
        self.init_layout(viewer_top_else_left)

    def init_view(self):
        self.scene = MyGraphicsScene()
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.viewport().installEventFilter(self)

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.mouse_press_view = QPoint()

        self.view.horizontalScrollBar().sliderMoved.connect(self.on_view_changed)
        self.view.verticalScrollBar().sliderMoved.connect(self.on_view_changed)
        self.scale_initializer_deffered_function = None
        self.slide_view_params = None
        self.slide_helper = None

    def init_labels(self, word_wrap):
        # word_wrap = True
        self.level_downsample_label = QLabel()
        self.level_downsample_label.setWordWrap(word_wrap)
        self.level_size_label = QLabel()
        self.level_size_label.setWordWrap(word_wrap)
        self.selected_rect_label = QLabel()
        self.selected_rect_label.setWordWrap(word_wrap)
        self.mouse_pos_scene_label = QLabel()
        self.mouse_pos_scene_label.setWordWrap(word_wrap)
        self.view_rect_scene_label = QLabel()
        self.view_rect_scene_label.setWordWrap(word_wrap)
        self.labels_layout = QVBoxLayout()
        self.labels_layout.setAlignment(Qt.AlignTop)
        self.labels_layout.addWidget(self.level_downsample_label)
        self.labels_layout.addWidget(self.level_size_label)
        self.labels_layout.addWidget(self.mouse_pos_scene_label)
        # self.labels_layout.addWidget(self.selected_rect_label)
        self.labels_layout.addWidget(self.view_rect_scene_label)

    def init_layout(self, viewer_top_else_left=True):
        main_layout = QVBoxLayout(self) if viewer_top_else_left else QHBoxLayout(self)
        main_layout.addWidget(self.view, )
        main_layout.addLayout(self.labels_layout)
        # main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    """
    If you want to start view frome some point at some level, specify <level> and <level_rect> params. 
    level_rect : rect in dimensions of slide at level=level. If None - fits the whole size of slide
    """

    def load(self, slide_view_params: SlideViewParams, preffered_rects_count=2000,
             zoom_step=1.15):
        self.zoom_step = zoom_step
        self.slide_view_params = slide_view_params
        self.slide_helper = SlideHelper(slide_view_params.slide_path)

        self.slide_graphics = SlideGraphicsGroup(slide_view_params, preffered_rects_count)
        self.scene.clear()
        self.scene.addItem(self.slide_graphics)

        if self.slide_view_params.level == -1 or self.slide_view_params.level is None:
            self.slide_view_params.level = self.slide_helper.get_max_level()

        self.slide_graphics.update_visible_level(self.slide_view_params.level)
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(self.slide_view_params.level))

        def scale_initializer_deffered_function():
            self.view.resetTransform()
            # print("size when loading: ", self.view.viewport().size())
            if self.slide_view_params.level_rect:
                # self.view.fitInView(QRectF(*self.slide_view_params.level_rect), Qt.KeepAspectRatioByExpanding)
                self.view.fitInView(QRectF(*self.slide_view_params.level_rect), Qt.KeepAspectRatio)
                # print("after fit: ", self.get_current_view_scene_rect())
            else:
                start_margins = QMarginsF(200, 200, 200, 200)
                start_image_rect_ = self.slide_helper.get_rect_for_level(self.slide_view_params.level)
                self.view.fitInView(start_image_rect_ + start_margins, Qt.KeepAspectRatio)

        self.scale_initializer_deffered_function = scale_initializer_deffered_function

    def eventFilter(self, qobj: 'QObject', event: QEvent):
        self.eventSignal.emit(event)
        event_processed = False
        # print("size when event: ", event, event.type(), self.view.viewport().size())
        if isinstance(event, QShowEvent):
            """
            we need it deffered because fitInView logic depends on current viewport size. Expecting at this point widget is finally resized before being shown at first
            """
            if self.scale_initializer_deffered_function:
                # TODO labels start to occupy some space after view was already fitted, and labels will reduce size of viewport
                # self.update_labels()
                self.scale_initializer_deffered_function()
                self.on_view_changed()
                self.scale_initializer_deffered_function = None
        elif isinstance(event, QWheelEvent):
            event_processed = self.process_viewport_wheel_event(event)
            # we handle wheel event to prevent GraphicsView interpret it as scrolling
        elif isinstance(event, QMouseEvent):
            event_processed = self.process_mouse_event(event)

        return event_processed

    def process_viewport_wheel_event(self, event: QWheelEvent):
        # print("size when wheeling: ", self.view.viewport().size())
        zoom_in = self.zoom_step
        zoom_out = 1 / zoom_in
        zoom_ = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.update_scale(event.pos(), zoom_)
        event.accept()
        self.on_view_changed()
        return True

    def process_mouse_event(self, event: QMouseEvent):
        if self.slide_helper is None:
            return False

        if event.button() == Qt.MiddleButton:
            if event.type() == QEvent.MouseButtonPress:
                self.slide_graphics.update_grid_visibility(not self.slide_graphics.slide_view_params.grid_visible)
                # items=self.scene.items()
                # QMessageBox.information(None, "Items", str(items))
                return True
            # self.update_scale(QPoint(), 1.15)
        elif event.button() == Qt.LeftButton:
            if event.type() == QEvent.MouseButtonPress:
                self.mouse_press_view = QPoint(event.pos())
                self.rubber_band.setGeometry(QRect(self.mouse_press_view, QSize()))
                self.rubber_band.show()
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.rubber_band.hide()
                self.remember_selected_rect_params()
                self.slide_graphics.update_selected_rect_0_level(self.slide_view_params.selected_rect_0_level)
                self.update_labels()
                self.scene.invalidate()
                return True
        elif event.type() == QEvent.MouseMove:
            self.mouse_pos_scene_label.setText(
                "mouse_scene: " + point_to_str(self.view.mapToScene(event.pos())))
            if not self.mouse_press_view.isNull():
                self.rubber_band.setGeometry(QRect(self.mouse_press_view, event.pos()).normalized())
            return True

        return False

    def remember_selected_rect_params(self):
        pos_scene = self.view.mapToScene(self.rubber_band.pos())
        rect_scene = self.view.mapToScene(self.rubber_band.rect()).boundingRect()
        downsample = self.slide_helper.get_downsample_for_level(self.slide_view_params.level)
        selected_qrectf_0_level = QRectF(pos_scene * downsample,
                                         rect_scene.size() * downsample)
        self.slide_view_params.selected_rect_0_level = selected_qrectf_0_level.getRect()

    def update_scale(self, mouse_pos: QPoint, zoom):
        old_mouse_pos_scene = self.view.mapToScene(mouse_pos)
        old_view_scene_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()

        old_level = self.get_best_level_for_scale(self.get_current_view_scale())
        old_level_downsample = self.slide_helper.get_downsample_for_level(old_level)
        new_level = self.get_best_level_for_scale(self.get_current_view_scale() * zoom)
        new_level_downsample = self.slide_helper.get_downsample_for_level(new_level)

        level_scale_delta = 1 / (new_level_downsample / old_level_downsample)

        r = old_view_scene_rect.topLeft()
        m = old_mouse_pos_scene
        new_view_scene_rect_top_left = (m - (m - r) / zoom) * level_scale_delta
        new_view_scene_rect = QRectF(new_view_scene_rect_top_left,
                                     old_view_scene_rect.size() * level_scale_delta / zoom)

        new_scale = self.get_current_view_scale() * zoom * new_level_downsample / old_level_downsample
        transform = QTransform().scale(new_scale, new_scale).translate(-new_view_scene_rect.x(),
                                                                       -new_view_scene_rect.y())

        new_rect = self.slide_helper.get_rect_for_level(new_level)
        self.scene.setSceneRect(new_rect)
        self.slide_view_params.level = new_level
        self.reset_view_transform()
        self.view.setTransform(transform, False)
        self.slide_graphics.update_visible_level(new_level)
        self.update_labels()

    def get_best_level_for_scale(self, scale):
        scene_width = self.scene.sceneRect().size().width()
        candidates = [0]
        for level in self.slide_helper.get_levels():
            w, h = self.slide_helper.get_level_size(level)
            if scene_width * scale <= w:
                candidates.append(level)
        best_level = max(candidates)
        return best_level

    def update_labels(self):
        level_downsample = self.slide_helper.get_downsample_for_level(self.slide_view_params.level)
        level_size = self.slide_helper.get_level_size(self.slide_view_params.level)
        self.level_downsample_label.setText(
            "level, downsample: {}, {:.0f}".format(self.slide_view_params.level,
                                                   level_downsample))
        self.level_size_label.setText("level_size: ({}, {})".format(*level_size))
        self.view_rect_scene_label.setText(
            "view_scene: ({:.0f},{:.0f},{:.0f},{:.0f})".format(*self.get_current_view_scene_rect().getRect()))
        if self.slide_view_params.selected_rect_0_level:
            self.selected_rect_label.setText(
                "selected rect (0-level): ({:.0f},{:.0f},{:.0f},{:.0f})".format(
                    *self.slide_view_params.selected_rect_0_level))

    def on_view_changed(self):
        if self.scale_initializer_deffered_function is None and self.slide_view_params:
            self.slide_view_params.level_rect = self.get_current_view_scene_rect().getRect()
        self.update_labels()

    def reset_view_transform(self):
        self.view.resetTransform()
        self.view.horizontalScrollBar().setValue(0)
        self.view.verticalScrollBar().setValue(0)

    def get_current_view_scene_rect(self):
        return self.view.mapToScene(self.view.viewport().rect()).boundingRect()

    def get_current_view_scale(self):
        scale = self.view.transform().m11()
        return scale
