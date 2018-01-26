class SlideTile:
    def __init__(self, slide_path=None, level=None, rect=None) -> None:
        super().__init__()
        self.slide_path = slide_path
        self.level = level
        self.rect = rect


class SlideViewParams:
    def __init__(self, slide_path=None, level=None, level_rect=None, grid_rects=None, grid_visible=False,
                 selected_rect_0_level=None) -> None:
        super().__init__()
        self.slide_path = slide_path
        self.level = level
        self.level_rect = level_rect
        self.grid_rects = grid_rects
        self.grid_visible = grid_visible
        self.selected_rect_0_level = selected_rect_0_level
