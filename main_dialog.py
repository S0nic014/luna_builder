
import imp
from PySide2 import QtCore
from PySide2 import QtWidgets
import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from luna import Logger
from luna import __version__
from luna.utils import pysideFn

from luna_builder.tabs import tab_workspace
import luna_builder.menus as menus
import luna_builder.editor.node_editor as node_editor
import luna_builder.editor.node_nodes_palette as node_nodes_palette

imp.reload(node_editor)
imp.reload(node_nodes_palette)


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    WINDOW_TITLE = "Luna builder v" + __version__
    DOCKED_TITLE = "Luna builder"
    UI_NAME = "lunaBuildManager"
    UI_SCRIPT = "import luna_builder\nluna_builder.MainDialog()"
    INSTANCE = None
    MINIMUM_SIZE = [400, 500]

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = MainDialog()

        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show(dockable=1, uiScript=cls.UI_SCRIPT)
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

    @classmethod
    def close_and_delete(cls):
        if not cls.INSTANCE:
            return
        cls.INSTANCE.close()
        cls.INSTANCE.deleteLater()
        cls.INSTANCE = None

    def showEvent(self, event):
        if self.isFloating():
            self.setWindowTitle(self.WINDOW_TITLE)
        else:
            self.setWindowTitle(self.DOCKED_TITLE)
        super(MainDialog, self).showEvent(event)

    def __init__(self):
        super(MainDialog, self).__init__()

        # Window adjustments
        self.__class__.INSTANCE = self
        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowIcon(pysideFn.get_QIcon("builder.svg"))
        self.setMinimumSize(*self.MINIMUM_SIZE)
        self.setProperty("saveWindowPref", True)

        # Workspace control
        self.workspaceControlName = "{0}WorkspaceControl".format(self.UI_NAME)
        pysideFn.add_widget_to_layout(self, self.workspaceControlName)

        # UI setup
        self.create_actions()
        self.create_widgets()
        self.create_menu_bar()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        pass

    def create_menu_bar(self):
        self.menu_bar = QtWidgets.QMenuBar()
        # Corner button
        self.update_tab_btn = QtWidgets.QPushButton()
        self.update_tab_btn.setFlat(True)
        self.update_tab_btn.setIcon(pysideFn.get_QIcon("refresh.png"))
        self.menu_bar.setCornerWidget(self.update_tab_btn, QtCore.Qt.TopRightCorner)

        # Menus
        self.file_menu = menus.FileMenu(self)
        self.edit_menu = menus.EditMenu(self)
        self.window_menu = menus.WindowMenu(self)
        self.controls_menu = menus.ControlsMenu()
        self.joints_menu = menus.JointsMenu()
        self.skin_menu = menus.SkinMenu()
        self.blendshapes_menu = menus.BlendshapesMenu()
        self.rig_menu = menus.RigMenu()
        self.help_menu = menus.HelpMenu(self)

        # Populate menu bar
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.edit_menu)
        self.menu_bar.addMenu(self.window_menu)
        self.menu_bar.addMenu(self.controls_menu)
        self.menu_bar.addMenu(self.joints_menu)
        self.menu_bar.addMenu(self.skin_menu)
        self.menu_bar.addMenu(self.blendshapes_menu)
        self.menu_bar.addMenu(self.rig_menu)
        self.menu_bar.addMenu(self.help_menu)

    def create_widgets(self):
        self.splitter_pallete_mdi = QtWidgets.QSplitter()
        self.nodes_palette = node_nodes_palette.NodesPalette()

        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.mdi_area.setDocumentMode(True)
        self.mdi_area.setTabsClosable(True)
        self.mdi_area.setTabsMovable(True)
        self.splitter_pallete_mdi.addWidget(self.nodes_palette)
        self.splitter_pallete_mdi.addWidget(self.mdi_area)

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabPosition(self.tab_widget.East)
        self.tab_widget.setMaximumWidth(500)
        self.tab_widget.setMinimumWidth(400)
        self.workspace_wgt = tab_workspace.WorkspaceWidget()
        self.tab_widget.addTab(self.workspace_wgt, self.workspace_wgt.label)

    def create_layouts(self):
        self.hor_layout = QtWidgets.QHBoxLayout()
        self.hor_layout.setContentsMargins(0, 0, 0, 0)
        self.hor_layout.addWidget(self.splitter_pallete_mdi)
        self.hor_layout.addWidget(self.tab_widget)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setMenuBar(self.menu_bar)
        self.main_layout.addLayout(self.hor_layout)

    def create_connections(self):
        # Other
        self.update_tab_btn.clicked.connect(lambda: self.tab_widget.currentWidget().update_data())
        self.update_tab_btn.clicked.connect(self.nodes_palette.update_node_tree)
        self.mdi_area.subWindowActivated.connect(self.update_title)

    @property
    def current_editor(self):
        if not self.current_window:
            return None
        editor = self.current_window.widget()  # type: node_editor.NodeEditor
        return editor

    @property
    def current_window(self):
        sub_wnd = self.mdi_area.currentSubWindow()  # type: QtWidgets.QMdiSubWindow
        return sub_wnd

    def create_mdi_child(self):
        new_editor = node_editor.NodeEditor()
        sub_wnd = self.mdi_area.addSubWindow(new_editor)  # type: QtWidgets.QMdiSubWindow
        # Signal connections
        new_editor.scene.signals.file_name_changed.connect(self.update_title)
        new_editor.scene.signals.modified.connect(self.update_title)
        new_editor.signals.about_to_close.connect(self.on_sub_window_close)
        return sub_wnd

    def find_mdi_child(self, file_name):
        for window in self.mdi_area.subWindowList():
            if window.widget().file_name == file_name:
                return window
        return None

    def set_active_sub_window(self, window):
        if window:
            self.mdi_area.setActiveSubWindow(window)

    def update_title(self):
        if not self.current_editor:
            self.setWindowTitle(self.WINDOW_TITLE)
            return

        friendly_title = self.current_editor.user_friendly_title
        self.setWindowTitle('{0} - {1}'.format(self.WINDOW_TITLE, friendly_title))

    def on_sub_window_close(self, widget, event):
        existing = self.find_mdi_child(widget.file_name)
        self.mdi_area.setActiveSubWindow(existing)

        if self.current_editor.maybe_save():
            event.accept()
        else:
            event.ignore()

    def on_build_open(self):
        sub_wnd = self.current_window if self.current_window else self.create_mdi_child()
        sub_wnd.widget().on_build_open()

    def on_build_open_tabbed(self):
        sub_wnd = self.create_mdi_child()
        res = sub_wnd.widget().on_build_open()
        if not res:
            self.mdi_area.removeSubWindow(sub_wnd)

    def on_build_new(self):
        try:
            sub_wnd = self.create_mdi_child()
            sub_wnd.show()
        except Exception:
            Logger.exception('Failed to create new build')

    def on_build_save(self):
        if self.current_editor:
            self.current_editor.on_build_save()

    def on_build_save_as(self):
        if self.current_editor:
            self.current_editor.on_build_save_as()


if __name__ == "__main__":
    try:
        if testTool and testTool.parent():  # noqa: F821
            workspaceControlName = testTool.parent().objectName()  # noqa: F821

            if pm.window(workspaceControlName, ex=1, q=1):
                pm.deleteUI(workspaceControlName)
    except Exception:
        pass

    testTool = MainDialog()
    testTool.show(dockable=1, uiScript="")
