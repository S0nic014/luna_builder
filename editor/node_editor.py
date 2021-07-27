import imp
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
from luna.workspace import Asset
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.node_scene as node_scene
import luna_builder.editor.node_node as node_node
import luna_builder.editor.graphics_view as graphics_view

# FIXME: TEST NODE IMPORTS
# import luna_builder.rig_nodes.base_component_nodes as component_nodes
# import luna_builder.rig_nodes.node_constant as node_constant
# import luna_builder.rig_nodes.node_sequence as node_sequence
# import luna_builder.rig_nodes.node_branch as node_branch

# # imp.reload(editor_conf)
# # imp.reload(node_scene)
# # imp.reload(node_node)
# # imp.reload(node_socket)
# # imp.reload(node_edge)
# # imp.reload(graphics_view)

# imp.reload(component_nodes)
# imp.reload(node_constant)
# imp.reload(node_sequence)
# imp.reload(node_branch)


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
        op_code = data_stream.readInt32()
        text = data_stream.readQString()
        # Position
        mouse_pos = event.pos()
        scene_pos = self.scene.view.mapToScene(mouse_pos)

        Logger.debug('''Dropped Item:
                       > OP_CODE: {0}
                       > TEXT: {1}
                       > MOUSE POS: {2}
                       > SCENE POS {3}'''.format(op_code, text, mouse_pos, scene_pos))

        # TODO: Replace with actual dragged node
        new_node = node_node.Node(self.scene,
                                  title=text,
                                  inputs=[editor_conf.DataType.COMPONENT, editor_conf.DataType.STRING, editor_conf.DataType.NUMERIC],
                                  outputs=[editor_conf.DataType.COMPONENT, editor_conf.DataType.STRING])
        new_node.set_position(scene_pos.x(), scene_pos.y())
        Logger.debug(new_node.gr_node)

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
        # node1 = node_node.Node(self.scene, inputs=[2, 2, 2], outputs=[3, 3, 3])
        # node2 = node_node.Node(self.scene, inputs=[3, 3, 3], outputs=[4, 4, 4])
        # node3 = node_node.Node(self.scene, inputs=[4, 4, 4], outputs=[2, 2, 2])
        # node1.set_position(-350, -250)
        # node2.set_position(-75, 0)
        # node3.set_position(200, -150)

        # edge1 = node_edge.Edge(self.scene, node1.outputs[0], node2.inputs[0])
        # edge2 = node_edge.Edge(self.scene, node2.outputs[0], node3.inputs[0])
        # comp1 = component_nodes.ComponentNode(self.scene)
        # anim_comp1 = component_nodes.AnimComponentNode(self.scene)
        # const1 = node_constant.ConstantNode(self.scene, data_type=editor_conf.DataType.STRING)
        # seq1 = node_sequence.SequenceNode(self.scene)
        # branch1 = node_branch.BranchNode(self.scene)

        self.scene.set_history_init_point()
