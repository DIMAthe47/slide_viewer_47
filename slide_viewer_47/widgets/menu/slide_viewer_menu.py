import json
import typing
from functools import singledispatch

from PIL import Image
import PIL
from PyQt5.QtCore import QRectF, QSize, QRect
from PyQt5.QtWidgets import QInputDialog, QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, \
    QHBoxLayout, QSpinBox, QWidget, QMessageBox

from PyQt5.QtGui import QPixmapCache, QColor
from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QMenu

from slide_viewer_47.common.level_builders import build_rects_and_color_alphas_for_grid
from slide_viewer_47.common.qt.my_action import MyAction
from slide_viewer_47.common.qt.my_menu import MyMenu
from slide_viewer_47.common.slide_view_params import SlideViewParams
from slide_viewer_47.widgets.menu.on_load_slide_action import OnLoadSlideAction
from slide_viewer_47.widgets.menu.slide_viewer_view_menu import SlideViewerViewMenu
from slide_viewer_47.widgets.slide_viewer import SlideViewer
from slide_viewer_47.common.screenshot_builders import build_screenshot_image


class SlideViewerMenu(MyMenu):
    def __init__(self, title, parent, slide_viewer: SlideViewer):
        super().__init__(title, parent)
        self.slide_viewer = slide_viewer
        self.load_action = OnLoadSlideAction("&load", self, slide_viewer)
        self.view_menu = SlideViewerViewMenu("&view", self, slide_viewer)
