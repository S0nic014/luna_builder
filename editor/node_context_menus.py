from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from luna import Logger
import luna_builder.editor.node_nodes_palette as node_nodes_palette


class NodeContextMenu(QtWidgets.QMenu):
    def __init__(self, editor):
        super(NodeContextMenu, self).__init__("Node", editor)
        self.scene = editor.scene

        self.create_actions()
        self.populate()
        self.create_connections()

    def create_actions(self):
        self.copy_action = QtWidgets.QAction("&Copy", self)
        self.cut_action = QtWidgets.QAction("&Cut", self)
        self.paste_action = QtWidgets.QAction("&Paste", self)
        self.delete_action = QtWidgets.QAction("&Delete", self)

    def create_connections(self):
        self.copy_action.triggered.connect(self.on_copy)
        self.cut_action.triggered.connect(self.on_cut)
        self.paste_action.triggered.connect(self.on_paste)
        self.delete_action.triggered.connect(self.on_delete)

    def populate(self):
        self.addAction(self.copy_action)
        self.addAction(self.cut_action)
        self.addAction(self.paste_action)
        self.addSeparator()
        self.addAction(self.delete_action)

    def on_copy(self):
        if self.scene:
            self.scene.copy_selected()

    def on_cut(self):
        if self.scene:
            self.scene.cut_selected()

    def on_paste(self):
        if self.scene:
            self.scene.paste_from_clipboard()

    def on_delete(self):
        if self.scene:
            self.scene.view.delete_selected()


class NodeCreatorMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, edge=None):
        super(NodeCreatorMenu, self).__init__(parent)
        tst = QtWidgets.QAction('Test', self)
        self.addAction(tst)


class NodeCreatorWidget(QtWidgets.QDialog):
    def __init__(self, view, parent=None, edge=None):
        super(NodeCreatorWidget, self).__init__(parent)
        self.view = view
        self.scene = view.scene

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.nodes_palette = node_nodes_palette.NodesPalette(icon_size=16)
        self.nodes_palette.nodes_tree.setDragEnabled(False)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.nodes_palette)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.nodes_palette.nodes_tree.itemClicked.connect(self.spawn_clicked_node)

    def spawn_clicked_node(self, item):
        if not item.parent():
            return

        node_id = item.data(0, node_nodes_palette.QLDragTreeWidget.NODE_ID_ROLE)
        json_data = self.nodes_palette.nodes_tree.get_item_json_data(item)
        # !FIXME Find position under cursor
        # position = self.view.mapToScene(QtGui.QCursor.pos())
        position = self.view.mapToScene(self.pos())

        new_node = self.scene.spawn_node_from_data(node_id, json_data, position)

        # Connect dragging edge
        if self.view.drag_edge and self.view.drag_edge.start_socket:
            socket_to_connect = new_node.find_first_input_with_label(self.view.drag_edge.start_socket.label)
            if not socket_to_connect:
                socket_to_connect = new_node.find_first_input_of_datatype(self.view.drag_edge.start_socket.data_type)
            self.view.end_edge_drag(socket_to_connect)
        self.close()
