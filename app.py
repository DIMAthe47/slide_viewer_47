import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog
from slide_viewer import SlideViewer


class SliderViewerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slide viewer')
        self.setMinimumSize(500, 600)
        self.slide_viewer = SlideViewer(zoom_step=1.15)
        self.setCentralWidget(self.slide_viewer)

        loadAction = QAction("load_slide", self)
        loadAction.triggered.connect(self.on_load_slide)
        menuBar = self.menuBar()
        menuBar.addAction(loadAction)

    def on_load_slide(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            self.slide_viewer.load_slide(file_path)

    def get_available_formats(self):
        return [
            ".svs",
            ".vms",
            ".vmu",
            ".ndpi",
            ".scn",
            ".mrx",
            ".tiff",
            ".svslide",
            ".tif",
            ".bif",
            ".mrxs",
            ".bif"]

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.NaDontUseNativeDialog
        file_ext_strings = ["*" + ext for ext in self.get_available_formats()]
        file_ext_string = " ".join(file_ext_strings)
        file_name, _ = QFileDialog.getOpenFileName(self, "Select whole-slide image to view", "",
                                                   "Whole-slide images ({});;".format(file_ext_string), options=options)
        return file_name


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cache_size_in_kb = 300 * 10 ** 3
    QPixmapCache.setCacheLimit(cache_size_in_kb)
    win = SliderViewerMainWindow()
    # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
    # slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    # slide_path = '/home/dimathe47/Downloads/OS-1.ndpi'
    # slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
    win.show()
    # win.slide_viewer.load_slide(slide_path)
    sys.exit(app.exec_())
