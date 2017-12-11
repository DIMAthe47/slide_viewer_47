import openslide
from PyQt5.QtCore import QPoint, Qt, QEvent, QRect, QSize, QRectF, QSizeF
from PyQt5.QtGui import QWheelEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel, QRubberBand, \
    QGraphicsItemGroup

from graphics_tile import GraphicsTile
from selected_graphics_rect import SelectedGraphicsRect
from utils import slice_rect, rect_to_str, point_to_str, SlideHelper


class SlideViewer(QWidget):
    def __init__(self, parent=None, zoom_step=1.15):
        super().__init__()
        self.zoom_step = zoom_step
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.level_label = QLabel()
        self.selected_rect_label = QLabel()
        self.mouse_pos_scene_label = QLabel()
        layout.addWidget(self.level_label)
        layout.addWidget(self.mouse_pos_scene_label)
        layout.addWidget(self.selected_rect_label)

        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.viewport().installEventFilter(self)
        self.view.items().clear()
        self.view.invalidateScene()

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.mouse_press_view = QPoint()

    def load_slide(self, slide_path, preffered_rects_count=2000):
        self.slide_path = slide_path
        self.slide = openslide.OpenSlide(slide_path)
        self.slide_helper = SlideHelper(self.slide)
        slide_w, slide_h = self.slide_helper.get_level_size_for_level(0)
        t = ((slide_w * slide_h) / preffered_rects_count) ** 0.5
        if t < 1000:
            t = 1000
        tile_size = (int(t), int(t))

        self.scene.clear()
        self.view.viewport().update()
        self.scene.invalidate()
        self.init_tiles_pyramid_models(tile_size)
        self.init_scale()

        self.selected_rect_downsample = 1
        self.selected_rect_pos_0 = QPoint(0, 0)
        self.selected_rect_size_0 = self.slide_helper.get_level_size_for_level(0)

    def init_tiles_pyramid_models(self, tile_size):
        self.tiles_pyramid_models = []
        for level in range(self.slide_helper.get_max_level() + 1):
            tiles_pyramid_model = self.build_tiles_pyramid_model(level, (tile_size[0], tile_size[1]))
            self.tiles_pyramid_models.append(tiles_pyramid_model)

    def init_scale(self):
        self.reset_transform()
        slide_rect_size = self.slide_helper.get_rect_for_level(self.slide_helper.get_max_level()).size()
        ratio = 1.25
        zoom_width = self.view.viewport().width() / (ratio * slide_rect_size.width())
        zoom_height = self.view.viewport().height() / (ratio * slide_rect_size.height())
        zoom_ = min([zoom_width, zoom_height])
        self.logical_zoom = 1 / self.slide_helper.get_downsample_for_level(self.slide_helper.get_max_level())
        self.level_relative_zoom = 1
        self.update_scale(QPoint(0, 0), zoom_)

    def eventFilter(self, qobj: 'QObject', event: 'QEvent'):
        # print(qobj, event)
        if isinstance(event, QWheelEvent):
            self.process_viewport_wheel_event(event)
            # we handle wheel event to prevent GraphicsView interpret it as scrolling
            return True
        elif isinstance(event, QMouseEvent):
            if event.button() == Qt.LeftButton:
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
                    "mouse_pos_scene: " + point_to_str(self.view.mapToScene(event.pos())))
                if not self.mouse_press_view.isNull():
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, event.pos()).normalized())
                return True

        return False

    def remember_selected_rect_params(self):
        pos_scene = self.view.mapToScene(self.rubber_band.pos() - self.view.pos())
        rect_scene = self.view.mapToScene(self.rubber_band.rect()).boundingRect()
        downsample = self.get_current_level_downsample()
        self.selected_qrectf_level = self.get_current_level_downsample()
        self.selected_qrectf_0_level = QRectF(pos_scene * downsample,
                                              QSizeF(rect_scene.size() * downsample))

    def update_selected_rect_view(self):
        for tiles_pyramid_model in self.tiles_pyramid_models:
            level = tiles_pyramid_model["level"]
            downsample = self.slide_helper.get_downsample_for_level(level)
            rect_for_level = QRectF(self.selected_qrectf_0_level.topLeft() / downsample,
                                    self.selected_qrectf_0_level.size() / downsample)
            selected_graphics_rect = SelectedGraphicsRect(rect_for_level)
            tiles_graphics_group = tiles_pyramid_model["tiles_graphics_group"]
            if tiles_pyramid_model["selected_graphics_rect"]:
                tiles_graphics_group.removeFromGroup(tiles_pyramid_model["selected_graphics_rect"])
            tiles_pyramid_model["selected_graphics_rect"] = selected_graphics_rect
            tiles_graphics_group.addToGroup(selected_graphics_rect)

        self.selected_rect_label.setText("selected rect (0-level): " + rect_to_str(self.selected_qrectf_0_level))

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
        self.level_relative_zoom *= zoom

        new_level_downsample = self.get_current_level_downsample()
        if old_level_downsample == new_level_downsample:
            self.update_scene_rect_for_current_level()

        new_mouse_pos_scene = self.view.mapToScene(mouse_pos)
        mouse_pos_delta = new_mouse_pos_scene - old_mouse_pos_scene
        pos_delta = mouse_pos_delta
        self.view.translate(pos_delta.x(), pos_delta.y())

        if old_level_downsample != new_level_downsample:
            new_view_pos_scene = self.view.mapToScene(self.view.rect().topLeft())
            level_scale_delta = 1 / (new_level_downsample / old_level_downsample)
            shift_scene = new_view_pos_scene
            shift_scene *= level_scale_delta
            self.reset_transform()
            self.update_scene_rect_for_current_level()
            scale_ = self.level_relative_zoom * new_level_downsample / old_level_downsample
            # scale_ comes from equation (size*zoom/downsample) == (new_size*new_zoom/new_downsample)
            self.view.scale(scale_, scale_)
            self.view.translate(-shift_scene.x(), -shift_scene.y())
            self.level_relative_zoom = scale_

        self.update_items_visibility_for_current_level()

    def get_current_level(self):
        return self.slide.get_best_level_for_downsample(1 / self.logical_zoom)

    def get_current_level_downsample(self):
        best_level = self.get_current_level()
        level_downsample = self.slide.level_downsamples[best_level]
        return level_downsample

    def update_scene_rect_for_current_level(self):
        best_level = self.get_current_level()
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(best_level))

    def update_items_visibility_for_current_level(self):
        best_level = self.get_current_level()
        level_downsample = self.slide.level_downsamples[best_level]
        for tile_pyramid_model in self.tiles_pyramid_models:
            if tile_pyramid_model["level"] == best_level:
                # tile_pyramid_model["tiles_graphics_group"].setZValue(100)
                tile_pyramid_model["tiles_graphics_group"].setVisible(True)
            else:
                tile_pyramid_model["tiles_graphics_group"].setVisible(False)
                # tile_pyramid_model["tiles_graphics_group"].setZValue(0)
        level_size = self.slide_helper.get_level_size_for_level(best_level)
        self.level_label.setText(
            "current level, downsample, size: {}, {:.4f}, ({}, {})".format(best_level, level_downsample, level_size[0],
                                                                           level_size[1]
                                                                           ))

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

    def build_tiles_pyramid_model(self, level, tile_size):
        tiles_rects = slice_rect(self.slide_helper.get_level_size_for_level(level), tile_size)
        tiles_graphics_group = QGraphicsItemGroup()
        for tile_rect in tiles_rects:
            downsample = self.slide_helper.get_downsample_for_level(level)
            item = GraphicsTile(tile_rect, self.slide, level, downsample)
            tiles_graphics_group.addToGroup(item)
        tiles_graphics_group.setVisible(False)
        self.scene.addItem(tiles_graphics_group)
        tile_pyramid_model = {
            "level": level,
            "tiles_graphics_group": tiles_graphics_group,
            "selected_graphics_rect": None
        }
        return tile_pyramid_model
