from PySide2 import QtWidgets
from luna import Logger


class EditMenu(QtWidgets.QMenu):
    def __init__(self, main_dialog, parent=None):
        super(EditMenu, self).__init__("&Edit", parent)
        self.main_dialog = main_dialog

        self.setTearOffEnabled(True)
        self.create_actions()
        self.populate()
        self.create_connections()

    @property
    def node_scene(self):
        return self.main_dialog.node_editor.scene

    @property
    def gr_view(self):
        return self.main_dialog.node_editor.gr_view

    def create_actions(self):
        self.undo_action = QtWidgets.QAction("&Undo", self)
        self.redo_action = QtWidgets.QAction("&Redo", self)
        self.copy_action = QtWidgets.QAction("&Copy", self)
        self.cut_action = QtWidgets.QAction("&Cut", self)
        self.paste_action = QtWidgets.QAction("&Paste", self)
        self.delete_action = QtWidgets.QAction("&Delete", self)

        self.undo_action.setShortcut('Ctrl+Z')
        self.redo_action.setShortcut('Ctrl+Y')
        self.copy_action.setShortcut('Ctrl+C')
        self.cut_action.setShortcut('Ctrl+X')
        self.paste_action.setShortcut('Ctrl+V')
        self.delete_action.setShortcut('Del')

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.undo_action.triggered.connect(self.on_undo)
        self.redo_action.triggered.connect(self.on_redo)
        self.copy_action.triggered.connect(self.on_copy)
        self.cut_action.triggered.connect(self.on_cut)
        self.paste_action.triggered.connect(self.on_paste)
        self.delete_action.triggered.connect(self.on_delete)

    def populate(self):
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addSeparator()
        self.addAction(self.copy_action)
        self.addAction(self.cut_action)
        self.addAction(self.paste_action)
        self.addSeparator()
        self.addAction(self.delete_action)

    def update_actions_state(self):
        is_scene_set = self.node_scene is not None
        self.undo_action.setEnabled(is_scene_set)
        self.redo_action.setEnabled(is_scene_set)
        self.copy_action.setEnabled(is_scene_set)
        self.cut_action.setEnabled(is_scene_set)
        self.paste_action.setEnabled(is_scene_set)
        self.delete_action.setEnabled(is_scene_set)

    def on_undo(self):
        if self.node_scene is not None:
            self.node_scene.history.undo()

    def on_redo(self):
        if self.node_scene is not None:
            self.node_scene.history.redo()

    def on_copy(self):
        pass

    def on_cut(self):
        pass

    def on_paste(self):
        pass

    def on_delete(self):
        self.gr_view.delete_selected()
