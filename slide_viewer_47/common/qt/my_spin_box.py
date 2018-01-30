import typing

from PyQt5.QtWidgets import QSpinBox, QWidget


class MySpinBox(QSpinBox):

    def __init__(self, start_value=0, max_value=2 ** 15, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMaximum(max_value)
        self.setValue(start_value)