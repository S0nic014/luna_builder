from PySide2 import QtWidgets
from luna import Logger
import luna_builder.editor.node_edge as node_edge


class WindowMenu(QtWidgets.QMenu):
    def __init__(self, main_window, parent=None):
        super(WindowMenu, self).__init__("&Window", parent)
        self.main_window = main_window

        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_actions(self):
        self.edge_type_group = QtWidgets.QActionGroup(self)
        self.edge_type_bezier_action = QtWidgets.QAction('Bezier', self)
        self.edge_type_direct_action = QtWidgets.QAction('Direct', self)
        self.edge_type_group.addAction(self.edge_type_bezier_action)
        self.edge_type_group.addAction(self.edge_type_direct_action)

        self.close_current_action = QtWidgets.QAction('Close', self)
        self.close_all_action = QtWidgets.QAction('Close All', self)
        self.tile_action = QtWidgets.QAction('Tile', self)
        self.next_wnd_action = QtWidgets.QAction('Next', self)
        self.previous_wnd_action = QtWidgets.QAction('Previous', self)

        self.edge_type_bezier_action.setCheckable(True)
        self.edge_type_direct_action.setCheckable(True)
        self.next_wnd_action.setShortcut('Ctrl+Tab')
        self.previous_wnd_action.setShortcut('Ctrl+Shift+Backtab')

    def create_sub_menus(self):
        self.scene_edge_type_menu = QtWidgets.QMenu("Edge style")

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        self.scene_edge_type_menu.aboutToShow.connect(self.update_edge_type_menu)
        self.edge_type_bezier_action.toggled.connect(self.on_bezier_edge_toggled)
        self.edge_type_direct_action.toggled.connect(self.on_direct_edge_toggled)
        # Actions
        self.close_current_action.triggered.connect(self.main_window.mdi_area.closeActiveSubWindow)
        self.close_all_action.triggered.connect(self.main_window.mdi_area.closeAllSubWindows)
        self.tile_action.triggered.connect(self.main_window.mdi_area.tileSubWindows)
        self.next_wnd_action.triggered.connect(self.main_window.mdi_area.activateNextSubWindow)
        self.previous_wnd_action.triggered.connect(self.main_window.mdi_area.activatePreviousSubWindow)

    def populate(self):
        self.addAction(self.main_window.nodes_palette_dock.toggleViewAction())
        self.addAction(self.main_window.vars_dock.toggleViewAction())
        self.addAction(self.main_window.workspace_dock.toggleViewAction())
        self.addAction(self.main_window.attrib_editor_dock.toggleViewAction())

        self.addMenu(self.scene_edge_type_menu)
        self.scene_edge_type_menu.addAction(self.edge_type_bezier_action)
        self.scene_edge_type_menu.addAction(self.edge_type_direct_action)

        self.addSeparator()
        self.addAction(self.close_current_action)
        self.addAction(self.close_all_action)
        self.addSeparator()
        self.addAction(self.tile_action)
        self.addSeparator()
        self.addAction(self.next_wnd_action)
        self.addAction(self.previous_wnd_action)

    def update_actions_state(self):
        has_mdi_child = self.main_window.current_editor is not None
        self.close_current_action.setEnabled(has_mdi_child)
        self.close_all_action.setEnabled(has_mdi_child)
        self.tile_action.setEnabled(has_mdi_child)
        self.next_wnd_action.setEnabled(has_mdi_child)
        self.previous_wnd_action.setEnabled(has_mdi_child)

    def update_edge_type_menu(self):
        if not self.main_window.current_editor:
            self.edge_type_bezier_action.setEnabled(False)
            self.edge_type_direct_action.setEnabled(False)
            return

        self.edge_type_bezier_action.setEnabled(True)
        self.edge_type_direct_action.setEnabled(True)
        bezier_selected = self.main_window.current_editor.scene.edge_type == node_edge.Edge.Type.BEZIER
        self.edge_type_bezier_action.setChecked(bezier_selected)
        self.edge_type_direct_action.setChecked(not bezier_selected)

    def on_bezier_edge_toggled(self, state):
        if not self.main_window.current_editor or not state:
            return

        self.main_window.current_editor.scene.edge_type = node_edge.Edge.Type.BEZIER

    def on_direct_edge_toggled(self, state):
        if not self.main_window.current_editor or not state:
            return

        self.main_window.current_editor.scene.edge_type = node_edge.Edge.Type.DIRECT
