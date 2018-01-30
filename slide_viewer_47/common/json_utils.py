import json
from functools import singledispatch

from PyQt5.QtCore import QRectF, QRect
from PyQt5.QtGui import QColor

from slide_viewer_47.common.slide_view_params import SlideViewParams


@singledispatch
def to_json(val):
    """Used by default."""
    return json.dumps(val, indent=4)


@to_json.register(QRectF)
def qrectf_to_json(val: QRectF):
    return json.dumps(val.getRect())


@to_json.register(QRect)
def qrect_to_json(val: QRect):
    return json.dumps(val.getRect())


@to_json.register(QColor)
def qcolor_to_json(val: QColor):
    return json.dumps(val.getRgb())


@to_json.register(SlideViewParams)
def slide_view_params_to_json(val: SlideViewParams):
    vars_ = dict(vars(val))
    del vars_["grid_rects_0_level"]
    del vars_["grid_colors_0_level"]
    return json.dumps(vars_, indent=4)
