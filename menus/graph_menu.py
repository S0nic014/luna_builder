from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class GraphMenu(QtWidgets.QMenu):
    def __init__(self, main_window, parent=None):
        super(GraphMenu, self).__init__("&Graph", parent)
        self.main_window = main_window

        self.setTearOffEnabled(True)
        self.create_actions()
        self.populate()
        self.create_connections()

    @property
    def executor(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.scene.executor

    @property
    def node_scene(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.scene

    @property
    def gr_view(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.gr_view

    def create_actions(self):
        self.execute_action = QtWidgets.QAction("&Execute", self)
        self.execute_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F5))

    def create_connections(self):
        self.main_window.mdi_area.subWindowActivated.connect(self.update_actions_state)
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.execute_action.triggered.connect(self.on_execute)

    def populate(self):
        self.addAction(self.execute_action)

    def update_actions_state(self):
        is_scene_set = self.node_scene is not None
        self.execute_action.setEnabled(is_scene_set)

    def on_execute(self):
        if self.executor is not None:
            self.executor.execute_graph()
