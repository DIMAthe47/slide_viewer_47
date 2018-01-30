from PyQt5.QtWidgets import QMainWindow

from slide_viewer_47.widgets.slide_viewer import SlideViewer
from slide_viewer_47.widgets.menu.slide_viewer_menu import SlideViewerMenu


class SlideViewerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slide viewer')
        self.resize(500, 600)
        self.slide_viewer = SlideViewer(viewer_top_else_left=True)
        self.setCentralWidget(self.slide_viewer)

        menuBar = self.menuBar()
        slide_viewer_menu = SlideViewerMenu("actions", menuBar, self.slide_viewer)
        menuBar.addMenu(slide_viewer_menu)
