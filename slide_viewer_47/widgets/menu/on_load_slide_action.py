from PyQt5.QtGui import QPixmapCache
from PyQt5.QtWidgets import QFileDialog

from slide_viewer_47.common.qt.my_action import MyAction
from slide_viewer_47.common.slide_view_params import SlideViewParams
from slide_viewer_47.widgets.slide_viewer import SlideViewer


class OnLoadSlideAction(MyAction):
    def __init__(self, title, parent, slide_viewer: SlideViewer):
        super().__init__(title, parent, self.on_load_slide)
        self.slide_viewer = slide_viewer

    def on_load_slide(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            # self.slide_viewer.load_slide(file_path, start_level=1, start_image_rect=QRectF(1000, 1000, 1000, 1000))
            slide_view_params = SlideViewParams(file_path)
            self.slide_viewer.load(slide_view_params)
            QPixmapCache.clear()

    def get_available_formats(self):
        whole_slide_formats = [
            "svs",
            "vms",
            "vmu",
            "ndpi",
            "scn",
            "mrx",
            "tiff",
            "svslide",
            "tif",
            "bif",
            "mrxs",
            "bif"]
        pillow_formats = [
            'bmp', 'bufr', 'cur', 'dcx', 'fits', 'fl', 'fpx', 'gbr',
            'gd', 'gif', 'grib', 'hdf5', 'ico', 'im', 'imt', 'iptc',
            'jpeg', 'jpg', 'jpe', 'mcidas', 'mic', 'mpeg', 'msp',
            'pcd', 'pcx', 'pixar', 'png', 'ppm', 'psd', 'sgi',
            'spider', 'tga', 'tiff', 'wal', 'wmf', 'xbm', 'xpm',
            'xv'
        ]
        available_formats = [*whole_slide_formats, *pillow_formats]
        available_extensions = ["." + available_format for available_format in available_formats]
        return available_extensions

    def open_file_name_dialog(self):
        # print(tuple([e[1:] for e in PIL.Image.EXTENSION]))
        options = QFileDialog.Options()
        file_ext_strings = ["*" + ext for ext in self.get_available_formats()]
        file_ext_string = " ".join(file_ext_strings)
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Select whole-slide image to view", "",
                                                   "Whole-slide images ({});;".format(file_ext_string),
                                                   options=options)
        return file_name
