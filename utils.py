import openslide
from PyQt5.QtCore import QRectF, QPoint, QPointF
from PyQt5.QtGui import QPolygonF


def slice_rect(rect_size, tile_size):
    tiles_rects = []
    x, y = (0, 0)
    x_size, y_size = rect_size
    x_step, y_step = tile_size
    while y < y_size:
        while x < x_size:
            w = x_step
            if x + w >= x_size:
                w = x_size - x
            h = y_step
            if y + h >= y_size:
                h = y_size - y
            tiles_rects.append((x, y, w, h))
            x += x_step
        x = 0
        y += y_step

        # print("rect_size", rect_size)
        # print("rects_sliced", tiles_rects)
    return tiles_rects


def rect_to_str(rect):
    if isinstance(rect, QPolygonF):
        rect = rect.boundingRect()
    if isinstance(rect, QRectF):
        return "({:.2f}, {:.2f}, {:.2f}, {:.2f})".format(rect.x(), rect.y(), rect.bottomRight().x(),
                                                         rect.bottomRight().y())
    else:
        return "({}, {}, {}, {})".format(rect.x(), rect.y(), rect.bottomRight().x(), rect.bottomRight().y())


def point_to_str(point: QPoint):
    if isinstance(point, QPointF):
        return "({:.2f}, {:.2f})".format(point.x(), point.y())
    else:
        return "({}, {})".format(point.x(), point.y())


class SlideHelper():
    def __init__(self, slide: openslide.OpenSlide):
        self.slide = slide

    def get_downsample_for_level(self, level):
        return self.slide.level_downsamples[level]

    def get_level_size(self, level):
        return self.slide.level_dimensions[level]

    def get_rect_for_level(self, level) -> QRectF:
        size_ = self.get_level_size(level)
        rect = QRectF(0, 0, size_[0], size_[1])
        return rect

    def get_max_level(self):
        return len(self.slide.level_downsamples) - 1

    def get_levels(self):
        return list(range(self.slide.level_count))

    def get_slide(self):
        return self.slide

    def get_best_level_for_downsample(self, downsample):
        return self.slide.get_best_level_for_downsample(downsample)


