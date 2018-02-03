from typing import List, Tuple

from slide_viewer_47.common.slide_helper import SlideHelper


class SlideViewParams:
    def __init__(self, slide_path: str = None, level: int = None, level_rect: Tuple[float, float, float, float] = None,
                 grid_rects_0_level: List[Tuple[float, float, float, float]] = None,
                 grid_color_alphas_0_level: List[int] = None,
                 grid_visible: bool = False,
                 selected_rect_0_level: Tuple[float, float, float, float] = None,
                 init_level_and_level_rect_if_none=True) -> None:
        super().__init__()
        self.slide_path = slide_path
        self.grid_rects_0_level = grid_rects_0_level
        self.grid_color_alphas_0_level = grid_color_alphas_0_level
        self.grid_visible = grid_visible
        self.selected_rect_0_level = selected_rect_0_level

        if (level is None or level_rect is None) and init_level_and_level_rect_if_none:
            slide_helper = SlideHelper(slide_path)
            level = slide_helper.get_max_level()
            level_rect = slide_helper.get_rect_for_level(level).getRect()

        self.level = level
        self.level_rect = level_rect

    def cache_key(self):
        cache_key_ = "{}_{}_{}_{}_{}_{}".format(self.slide_path,
                                                self.level,
                                                self.level_rect, id(self.grid_rects_0_level),
                                                id(self.grid_color_alphas_0_level),
                                                self.grid_visible)
        return cache_key_

    # def __str__(self) -> str:
    #     return str(vars(self))
#
