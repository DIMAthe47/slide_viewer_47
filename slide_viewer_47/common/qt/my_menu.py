from PyQt5.QtWidgets import QAction, QMenu, QMenuBar


class MyMenu(QMenu):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.window = None
        if isinstance(parent, QMenu) or isinstance(parent, QMenuBar):
            self.window = parent.parent()
            parent.addMenu(self)
