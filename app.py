import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QMenuBar
from slide_viewer import SlideViewer
from slide_viewer_menu import SlideViewerMenu


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


sys.excepthook = excepthook


class SliderViewerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slide viewer')
        # self.resize(500, 600)
        self.resize(200, 200)
        # self.setGeometry()
        # self.setFixedSize(500,600)
        # self.setMinimumSize(500, 600)
        self.slide_viewer = SlideViewer(zoom_step=1.15)
        self.setCentralWidget(self.slide_viewer)

        menuBar = self.menuBar()
        slide_viewer_menu = SlideViewerMenu(menuBar)
        slide_viewer_menu.set_slide_viewer(self.slide_viewer)
        menuBar.addMenu(slide_viewer_menu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cache_size_in_kb = 700 * 10 ** 3
    QPixmapCache.setCacheLimit(cache_size_in_kb)
    win = SliderViewerMainWindow()
    # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
    # slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    # slide_path = '/home/dimathe47/Downloads/OS-1.ndpi'
    # slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
    slide_path = r'C:\Users\DIMA\PycharmProjects\slide_cbir_47\downloads\images\19403.svs'
    win.show()
    win.slide_viewer.load_slide(slide_path)
    # win.slide_viewer.update_grid_size((224,224))
    sys.exit(app.exec_())
