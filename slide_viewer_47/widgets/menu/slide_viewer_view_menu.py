from PyQt5.QtCore import QRectF, QSize
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLineEdit, \
    QHBoxLayout, QSpinBox, QMessageBox

from slide_viewer_47.common.json_utils import to_json
from slide_viewer_47.common.level_builders import build_rects_and_colors_for_grid
from slide_viewer_47.common.qt.my_action import MyAction
from slide_viewer_47.common.qt.my_menu import MyMenu
from slide_viewer_47.common.qt.my_spin_box import MySpinBox
from slide_viewer_47.widgets.slide_viewer import SlideViewer
from slide_viewer_47.common.screenshot_builders import build_screenshot_image


class SlideViewerViewMenu(MyMenu):
    def __init__(self, title, parent, slide_viewer: SlideViewer):
        super().__init__(title, parent)

        self.slide_viewer = slide_viewer

        self.grid_action = MyAction("set gri&d size", self, self.on_set_grid_action)
        self.toggle_grid_action = MyAction("&toggle grid", self, self.on_toggle_grid_action)
        self.go_to_action = MyAction("&go to", self, self.on_go_to_action)
        self.take_screenshot_action = MyAction("&screenshot", self, self.on_take_screenshot_action)
        self.print_items_action = MyAction("print &items", self, self.on_print_items_action)
        self.print_slide_view_params_action = MyAction("print slide_&view_params", self,
                                                       self.on_print_slide_view_params)

    def on_print_items_action(self):
        items = self.slide_viewer.scene.items(self.slide_viewer.get_current_view_scene_rect())
        print(items)
        QMessageBox.information(None, "Items", str(items))

    def on_print_slide_view_params(self):
        str_ = to_json(self.slide_viewer.slide_view_params)
        print(str_)
        QMessageBox.information(None, "SlideViewParams", str_)

    def on_set_grid_action(self):
        dialog = QDialog()
        dialog.setWindowTitle("Grid size")

        # grid_size = self.slide_viewer.slide_graphics.slide_view_params.grid_size_0_level
        # if not grid_size:
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
            rects, colors = build_rects_and_colors_for_grid((grid_w.value(), grid_h.value()),
                                                            self.slide_viewer.slide_helper.get_level_size(0))
            self.slide_viewer.slide_graphics.update_grid_rects_0_level(rects, colors)

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
            image.save(filepath.text())

    def on_toggle_grid_action(self):
        self.slide_viewer.slide_graphics.update_grid_visibility(
            not self.slide_viewer.slide_graphics.slide_view_params.grid_visible)
