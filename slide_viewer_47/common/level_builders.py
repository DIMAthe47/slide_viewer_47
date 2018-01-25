import random

from PyQt5.QtGui import QColor

from slide_viewer_47.common.utils import SlideHelper, slice_rect
from slide_viewer_47.graphics.graphics_grid import GraphicsGrid
from slide_viewer_47.graphics.graphics_tile import GraphicsTile
from slide_viewer_47.graphics.my_graphics_group import MyGraphicsGroup


def build_tiles_level(level, tile_size, slide_helper: SlideHelper):
    level_size = slide_helper.get_level_size(level)
    tiles_rects = slice_rect(level_size, tile_size)
    tiles_graphics_group = MyGraphicsGroup()
    downsample = slide_helper.get_downsample_for_level(level)
    for tile_rect in tiles_rects:
        item = GraphicsTile(tile_rect, slide_helper.get_slide_path(), level, downsample)
        item.moveBy(tile_rect[0], tile_rect[1])
        tiles_graphics_group.addToGroup(item)

    return tiles_graphics_group


def build_grid_level(level, grid_size_0_level, slide_helper: SlideHelper):
    level_size = slide_helper.get_level_size(level)
    level_downsample = slide_helper.get_downsample_for_level(level)
    rect_size = grid_size_0_level[0] / level_downsample, grid_size_0_level[1] / level_downsample
    rects = slice_rect(level_size, rect_size)

    colors = [QColor(0, 255, 0, random.randint(0, 128)) for i in range(len(rects))]
    graphics_grid = GraphicsGrid(rects, colors, [0, 0, *level_size])
    return graphics_grid


def build_grid_level_from_rects(level, rects, colors, slide_helper: SlideHelper):
    level_size = slide_helper.get_level_size(level)
    graphics_grid = GraphicsGrid(rects, colors, [0, 0, *level_size])
    return graphics_grid
