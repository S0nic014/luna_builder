from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import luna.utils.pysideFn as pysideFn


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
        self.reset_stepped_execution = QtWidgets.QAction("&Reset stepped execution", self)
        self.execute_step_action = QtWidgets.QAction("&Execute Step", self)
        self.execute_action = QtWidgets.QAction(pysideFn.get_QIcon('execute.png'), "&Execute", self)

        self.execute_step_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F6))
        self.execute_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F5))

    def create_connections(self):
        self.main_window.mdi_area.subWindowActivated.connect(self.update_actions_state)
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.reset_stepped_execution.triggered.connect(self.on_reset_stepped_execution)
        self.execute_step_action.triggered.connect(self.on_execute_step)
        self.execute_action.triggered.connect(self.on_execute)

    def populate(self):
        self.addAction(self.reset_stepped_execution)
        self.addAction(self.execute_step_action)
        self.addSeparator()
        self.addAction(self.execute_action)

    def update_actions_state(self):
        is_scene_set = self.node_scene is not None
        self.reset_stepped_execution.setEnabled(is_scene_set)
        self.execute_step_action.setEnabled(is_scene_set)
        self.execute_action.setEnabled(is_scene_set)

    def on_execute(self):
        if self.executor is not None:
            self.executor.execute_graph()

    def on_execute_step(self):
        if self.executor is not None:
            self.executor.execute_step()

    def on_reset_stepped_execution(self):
        if self.executor is not None:
            self.executor.reset_stepped_execution()
