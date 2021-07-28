import os
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
import luna.static.directories as directories
import luna_builder.editor.editor_conf as editor_conf


class NodesPalette(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(NodesPalette, self).__init__('Nodes Palette', parent)

        self.setMinimumWidth(190)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.update_node_tree()

    def create_widgets(self):
        self.nodes_tree = QLDragTreeWidget()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.nodes_tree)

    def create_connections(self):
        pass

    def update_node_tree(self):
        self.nodes_tree.clear()
        self.add_registered_nodes()

    def add_registered_nodes(self):
        keys = list(editor_conf.NODE_REGISTER.keys())
        keys.sort()
        for node_id in keys:
            node_class = editor_conf.NODE_REGISTER[node_id]
            self.nodes_tree.add_node_item(node_id, node_class.DEFAULT_TITLE, category=node_class.CATEGORY, icon_name=node_class.ICON)


class QLDragTreeWidget(QtWidgets.QTreeWidget):

    PIXMAP_ROLE = QtCore.Qt.UserRole
    NODE_ID_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None):
        super(QLDragTreeWidget, self).__init__(parent)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

    def add_node_item(self, node_id, label_text, category='Undefiend', icon_name=None):
        if not icon_name:
            icon_name = 'func.png'
        icon_path = os.path.join(directories.ICONS_PATH, icon_name)
        pixmap = QtGui.QPixmap(icon_path)

        # Find paren
        parent_item = self.findItems(category, QtCore.Qt.MatchContains)
        parent_item = parent_item[0] if parent_item else self.add_category(category)

        # Setup item
        item = QtWidgets.QTreeWidgetItem()
        parent_item.addChild(item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
        item.setText(0, label_text)
        item.setIcon(0, QtGui.QIcon(pixmap))
        item.setSizeHint(0, QtCore.QSize(32, 32))
        # Setup item
        item.setData(0, QLDragTreeWidget.PIXMAP_ROLE, pixmap)
        item.setData(0, QLDragTreeWidget.NODE_ID_ROLE, node_id)

    def add_category(self, name, expanded=True):
        tree_item = QtWidgets.QTreeWidgetItem(self)
        tree_item.setText(0, name.capitalize())
        tree_item.setExpanded(True)
        return tree_item

    def startDrag(self, event):
        Logger.debug('Palette::startDrag')
        try:
            item = self.currentItem()  # type: QtWidgets.QTreeWidgetItem
            node_id = item.data(0, QLDragTreeWidget.NODE_ID_ROLE)
            pixmap = QtGui.QPixmap(item.data(0, QLDragTreeWidget.PIXMAP_ROLE))

            # Pack item data
            item_data = QtCore.QByteArray()
            data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
            data_stream << pixmap
            data_stream.writeInt32(node_id)
            data_stream.writeQString(item.text(0))

            # Create mime data
            mime_data = QtCore.QMimeData()
            mime_data.setData(editor_conf.PALETTE_MIMETYPE, item_data)

            # Create drag
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
            drag.setPixmap(pixmap)

            Logger.debug('Dragging item <{0}>, {1}'.format(node_id, item))
            drag.exec_(QtCore.Qt.MoveAction)

        except Exception:
            Logger.exception('Palette drag exception')
