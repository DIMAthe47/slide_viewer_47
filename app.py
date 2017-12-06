import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow
from slide_viewer import SlideViewer


class SliderViewerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slide viewer')
        self.setMinimumSize(500, 600)
        self.slide_viewer = SlideViewer(zoom_step=1.15)
        self.setCentralWidget(self.slide_viewer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cache_size_in_kb = 300 * 10 ** 3
    QPixmapCache.setCacheLimit(cache_size_in_kb)
    win = SliderViewerMainWindow()
    # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
    # slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    slide_path = '/home/dimathe47/Downloads/OS-1.ndpi'
    # slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
    win.show()
    win.slide_viewer.load_slide(slide_path)
    sys.exit(app.exec_())
