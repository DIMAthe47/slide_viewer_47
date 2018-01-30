from PyQt5.QtWidgets import QAction, QMenu


class MyAction(QAction):
    def __init__(self, title, parent, action_func):
        super().__init__(title, parent)
        self.window = None
        if isinstance(parent, QMenu):
            self.window = parent.parent()
            parent.addAction(self)
        self.triggered.connect(action_func)
