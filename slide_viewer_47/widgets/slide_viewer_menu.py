import typing

from PIL import Image
import PIL
from PyQt5.QtCore import QRectF, QSize
from PyQt5.QtWidgets import QInputDialog, QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, \
    QHBoxLayout, QSpinBox, QWidget, QMessageBox

from PyQt5.QtGui import QPixmapCache
from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QMenu

from slide_viewer_47.common.slide_tile import SlideViewParams
from slide_viewer_47.widgets.slide_viewer import SlideViewer
from slide_viewer_47.common.screenshot_builders import build_screenshot_image


class MySpinBox(QSpinBox):

    def __init__(self, start_value=0, max_value=2 ** 15, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMaximum(max_value)
        self.setValue(start_value)


class SlideViewerMenu(QMenu):
    def __init__(self, parent, title="&slide"):
        super().__init__(title, parent)
        self.loadAction = QAction("&load", parent)
        self.addAction(self.loadAction)
        self.loadAction.triggered.connect(self.on_load_slide)
        self.grid_action = QAction("set gri&d size", parent)
        self.addAction(self.grid_action)
        self.grid_action.triggered.connect(self.on_set_grid_action)
        self.toggle_grid_action = QAction("&toggle grid", parent)
        self.toggle_grid_action.triggered.connect(self.on_toggle_grid_action)
        self.addAction(self.toggle_grid_action)
        self.go_to_action = QAction("&go to", parent)
        self.go_to_action.triggered.connect(self.on_go_to_action)
        self.addAction(self.go_to_action)
        self.take_screenshot_action = QAction("&screenshot", parent)
        self.take_screenshot_action.triggered.connect(self.on_take_screenshot_action)
        self.addAction(self.take_screenshot_action)
        self.slide_viewer: SlideViewer = None

        self.print_items_action = QAction("&print items", parent)
        self.print_items_action.triggered.connect(self.on_print_items_action)
        self.addAction(self.print_items_action)

    def set_slide_viewer(self, slide_viewer: SlideViewer):
        self.slide_viewer = slide_viewer

    def on_print_items_action(self):
        items = self.slide_viewer.scene.items()
        print(items)
        QMessageBox.information(None, "Items", str(items))

    def on_load_slide(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            # self.slide_viewer.load_slide(file_path, start_level=1, start_image_rect=QRectF(1000, 1000, 1000, 1000))
            slide_view_params = SlideViewParams(file_path)
            self.slide_viewer.load(slide_view_params)
            QPixmapCache.clear()

    def on_set_grid_action(self):
        dialog = QDialog()
        dialog.setWindowTitle("Grid size")

        grid_size = self.slide_viewer.slide_graphics.grid_size_0_level
        if not grid_size:
            grid_size = (224, 224)

        grid_w = QSpinBox()
        grid_w.setMaximum(2 ** 15)
        grid_w.setValue(grid_size[0])

        grid_h = QSpinBox()
        grid_h.setMaximum(2 ** 15)
        grid_h.setValue(grid_size[1])

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(grid_w)
        horizontal_layout.addWidget(grid_h)
        form_layout = QFormLayout()
        form_layout.addRow("grid width:", horizontal_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        main_layout.addWidget(button_box)
        dialog.setLayout(main_layout)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        res = dialog.exec()
        if res == QDialog.Accepted:
            self.slide_viewer.slide_graphics.update_grid_size_0_level((grid_w.value(), grid_h.value()))

    def on_go_to_action(self):
        dialog = QDialog()
        dialog.setWindowTitle("Go to")

        level = MySpinBox(1)
        x = MySpinBox(1000)
        y = MySpinBox(1000)
        width = MySpinBox(1000)
        height = MySpinBox(1000)

        form_layout = QFormLayout()
        form_layout.addRow("level:", level)
        form_layout.addRow("x:", x)
        form_layout.addRow("y:", y)
        form_layout.addRow("width:", width)
        form_layout.addRow("height:", height)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        main_layout.addWidget(button_box)
        dialog.setLayout(main_layout)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        res = dialog.exec()
        if res == QDialog.Accepted:
            slide_path = self.slide_viewer.slide_helper.get_slide_path()
            qrectf = QRectF(x.value(), y.value(), width.value(), height.value())
            self.slide_viewer.load_slide(slide_path, level.value(), qrectf)

    def on_take_screenshot_action(self):
        dialog = QDialog()
        dialog.setWindowTitle("Screenshot")

        width = MySpinBox(1000)
        height = MySpinBox(1000)
        filepath = QLineEdit("screenshot_from_menu.jpg")

        form_layout = QFormLayout()
        form_layout.addRow("width:", width)
        form_layout.addRow("height:", height)
        form_layout.addRow("filepath:", filepath)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        main_layout.addWidget(button_box)
        dialog.setLayout(main_layout)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        res = dialog.exec()
        if res == QDialog.Accepted:
            image = build_screenshot_image(self.slide_viewer.scene, QSize(width.value(), height.value()),
                                           self.slide_viewer.get_current_view_scene_rect())
            self.slide_viewer.scene.views()
            image.save(filepath.text())

    def on_toggle_grid_action(self):
        self.slide_viewer.slide_graphics.update_grid_visibility(
            not self.slide_viewer.slide_graphics.grid_visible)

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
        file_name, _ = QFileDialog.getOpenFileName(self, "Select whole-slide image to view", "",
                                                   "Whole-slide images ({});;".format(file_ext_string),
                                                   options=options)
        return file_name
