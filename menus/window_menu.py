from PySide2 import QtWidgets
from luna import Logger


class WindowMenu(QtWidgets.QMenu):
    def __init__(self, main_dialog, parent=None):
        super(WindowMenu, self).__init__("&Window", parent)
        self.main_dialog = main_dialog

        self.setTearOffEnabled(True)
        self.create_actions()
        self.populate()
        self.create_connections()

    def create_actions(self):
        self.nodes_palette_action = QtWidgets.QAction('Nodes Palette', self)
        self.nodes_palette_action.setCheckable(True)
        self.close_current_action = QtWidgets.QAction('Close', self)
        self.close_all_action = QtWidgets.QAction('Close All', self)
        self.tile_action = QtWidgets.QAction('Tile', self)
        self.next_wnd_action = QtWidgets.QAction('Next', self)
        self.previous_wnd_action = QtWidgets.QAction('Previous', self)

        self.next_wnd_action.setShortcut('Ctrl+Tab')
        self.previous_wnd_action.setShortcut('Ctrl+Shift+Backtab')

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.nodes_palette_action.triggered.connect(self.toggle_nodes_palette)
        self.close_current_action.triggered.connect(self.main_dialog.mdi_area.closeActiveSubWindow)
        self.close_all_action.triggered.connect(self.main_dialog.mdi_area.closeAllSubWindows)
        self.tile_action.triggered.connect(self.main_dialog.mdi_area.tileSubWindows)
        self.next_wnd_action.triggered.connect(self.main_dialog.mdi_area.activateNextSubWindow)
        self.previous_wnd_action.triggered.connect(self.main_dialog.mdi_area.activatePreviousSubWindow)

    def populate(self):
        self.addAction(self.nodes_palette_action)
        self.addSeparator()
        self.addAction(self.close_current_action)
        self.addAction(self.close_all_action)
        self.addSeparator()
        self.addAction(self.tile_action)
        self.addSeparator()
        self.addAction(self.next_wnd_action)
        self.addAction(self.previous_wnd_action)

    def update_actions_state(self):
        self.nodes_palette_action.setChecked(self.main_dialog.nodes_palette.isVisible())
        has_mdi_child = self.main_dialog.current_editor is not None
        self.close_current_action.setEnabled(has_mdi_child)
        self.close_all_action.setEnabled(has_mdi_child)
        self.tile_action.setEnabled(has_mdi_child)
        self.next_wnd_action.setEnabled(has_mdi_child)
        self.previous_wnd_action.setEnabled(has_mdi_child)

    def toggle_nodes_palette(self):
        self.main_dialog.nodes_palette.setVisible(not self.main_dialog.nodes_palette.isVisible())
