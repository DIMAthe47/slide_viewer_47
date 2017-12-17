from PyQt5.QtGui import QPixmapCache
from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QMenu


class SlideViewerMenu(QMenu):
    def __init__(self, parent, title="slide"):
        super().__init__(title, parent)
        self.loadAction = QAction("load", parent)
        self.addAction(self.loadAction)
        self.loadAction.triggered.connect(self.on_load_slide)
        self.slide_viewer = None

    def set_slide_viewer(self, slide_viewer):
        self.slide_viewer = slide_viewer

    def on_load_slide(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            self.slide_viewer.load_slide(file_path)
            QPixmapCache.clear()

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
