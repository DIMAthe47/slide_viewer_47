import openslide
from PyQt5.QtCore import QRectF


class SlideHelper():
    def __init__(self, slide_path: str):
        self.slide_path = slide_path
        with openslide.open_slide(slide_path) as slide:
            self.level_downsamples = slide.level_downsamples
            self.level_dimensions = slide.level_dimensions
            self.level_count = slide.level_count

    def get_slide_path(self):
        return self.slide_path

    def get_downsample_for_level(self, level):
        return self.level_downsamples[level]

    def get_level_size(self, level):
        return self.level_dimensions[level]

    def get_rect_for_level(self, level) -> QRectF:
        size_ = self.get_level_size(level)
        rect = QRectF(0, 0, size_[0], size_[1])
        return rect

    def get_max_level(self):
        return len(self.level_downsamples) - 1

    def get_levels(self):
        return list(range(self.level_count))

    def get_best_level_for_downsample(self, downsample):
        with openslide.open_slide(self.slide_path) as slide:
            return slide.get_best_level_for_downsample(downsample)