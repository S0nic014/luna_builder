import imp
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
from luna.workspace import Asset
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.node_scene as node_scene
import luna_builder.editor.graphics_view as graphics_view

imp.reload(node_scene)
imp.reload(graphics_view)


class EditorSignals(QtCore.QObject):
    about_to_close = QtCore.Signal(QtWidgets.QWidget, QtCore.QEvent)


class NodeEditor(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.signals = EditorSignals()
        self.init_ui()
        self.add_debug_nodes()

    def init_ui(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(200, 500)
        self.create_widgets()
        self.create_layouts()
        self.create_conections()
        self.update_title()

    def create_widgets(self):
        # Graphics scene
        self.scene = node_scene.Scene()

        # Graphics view
        self.gr_view = graphics_view.QLGraphicsView(self.scene.gr_scene, self)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.gr_view)

    def create_conections(self):
        self.scene.signals.file_name_changed.connect(self.update_title)
        self.scene.signals.modified.connect(self.update_title)
        self.scene.signals.item_drag_entered.connect(self.on_item_drag_enter)
        self.scene.signals.item_dropped.connect(self.on_item_drop)

    # ======== Properties ======== #
    @property
    def file_name(self):
        return self.scene.file_name

    @property
    def file_base_name(self):
        name = self.scene.file_base_name
        if not name:
            return 'Untitled'
        return name

    @property
    def user_friendly_title(self):
        filename = self.file_base_name
        if self.scene.has_been_modified:
            filename += '*'
        return filename

    # ======== Events ======== #

    def closeEvent(self, event):
        self.signals.about_to_close.emit(self, event)

    # ======== Drag & Drop ======== #

    def on_item_drag_enter(self, event):
        Logger.debug('On item drag enter')
        if event.mimeData().hasFormat(editor_conf.PALETTE_MIMETYPE):
            event.acceptProposedAction()
        else:
            Logger.warning('Unsupported item: {0}'.format(event.mimeData().text()))
            event.setAccepted(False)

    def on_item_drop(self, event):
        Logger.debug('On item drop')
        if not event.mimeData().hasFormat(editor_conf.PALETTE_MIMETYPE):
            Logger.warning('Unsupported item format: {0}'.format(event.mimeData().text()))
            event.ignore()
            return

        # Retrive data from droped item
        event_data = event.mimeData().data(editor_conf.PALETTE_MIMETYPE)
        data_stream = QtCore.QDataStream(event_data, QtCore.QIODevice.ReadOnly)
        pixmap = QtGui.QPixmap()
        data_stream >> pixmap
        node_id = data_stream.readInt32()
        func_signature = data_stream.readQString()
        text = data_stream.readQString()
        # Position
        mouse_pos = event.pos()
        scene_pos = self.scene.view.mapToScene(mouse_pos)

        Logger.debug('''Dropped Item:
                       > NODE_ID: {node_id}
                       > FUNC: {func_signature}
                       > TEXT: {text}
                       > MOUSE POS: {mouse_pos}
                       > SCENE POS {scene_pos}'''.format(node_id=node_id, func_signature=func_signature, text=text, mouse_pos=mouse_pos, scene_pos=scene_pos))

        try:
            new_node = editor_conf.get_node_class_from_id(node_id)(self.scene)
            new_node.set_position(scene_pos.x(), scene_pos.y())
            self.scene.history.store_history('Created Node {0}'.format(new_node.as_str(name_only=True)))
        except Exception:
            Logger.exception('Failed to instansiate dropped node')

        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    # ======== Methods ======== #

    def update_title(self):
        self.setWindowTitle(self.user_friendly_title)

    def is_modified(self):
        return self.scene.has_been_modified

    def maybe_save(self):
        if not self.is_modified():
            return True

        res = QtWidgets.QMessageBox.warning(self, 'Warning: Build not saved',
                                            'Save changes to current build?',
                                            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        if res == QtWidgets.QMessageBox.Save:
            return self.on_build_save()
        if res == QtWidgets.QMessageBox.Cancel:
            return False
        return True

    def on_build_new(self):
        if self.maybe_save():
            self.scene.clear()
            self.scene.file_name = None

    def on_build_open(self):
        if not Asset.get():
            Logger.warning('Asset is not set')
            return
        if not self.maybe_save():
            return

        rig_filter = "Rig Build (*.rig)"
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open rig build scene", Asset.get().build, rig_filter)[0]
        if not file_path:
            return False
        self.scene.load_from_file(file_path)
        return True

    def on_build_save(self):
        if not Asset.get():
            Logger.warning('Asset is not set')
            return

        res = True
        if self.scene.file_name:
            self.scene.save_to_file(self.scene.file_name)
        else:
            res = self.on_build_save_as()
        return res

    def on_build_save_as(self):
        if not Asset.get():
            Logger.warning('Asset is not set')
            return

        rig_filter = "Rig Build (*.rig)"
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save build graph to file', Asset.get().new_build_path, rig_filter)[0]
        if not file_path:
            return False
        self.scene.save_to_file(file_path)
        return True

    def add_debug_nodes(self):
        # Test nodes

        self.scene.set_history_init_point()
