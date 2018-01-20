import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication
from widgets.slide_viewer_main_window import SlideViewerMainWindow

def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)

sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cache_size_in_kb = 700 * 10 ** 3
    QPixmapCache.setCacheLimit(cache_size_in_kb)
    win = SlideViewerMainWindow()
    # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
    # slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    # slide_path = '/home/dimathe47/Downloads/OS-1.ndpi'
    # slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
    slide_path = r'C:\Users\DIMA\PycharmProjects\slide_cbir_47\downloads\images\19403.svs'
    win.show()
    win.slide_viewer.load_slide(slide_path)
    # win.slide_viewer.update_grid_size((224,224))
    sys.exit(app.exec_())
