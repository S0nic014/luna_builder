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

        self.setMinimumWidth(170)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # TODO: Replace with actual node items
        self.add_test_items()

    def create_widgets(self):
        self.nodes_list = QLDragListBox()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.nodes_list)

    def create_connections(self):
        pass

    def add_test_items(self):
        self.nodes_list.add_node_item('Character Component', 'body.png', op_code=editor_conf.NODE_REGISTER.get('Character Component'))
        self.nodes_list.add_node_item('Simple Component', 'body.png', op_code=editor_conf.NODE_REGISTER.get('Simple Component'))
        self.nodes_list.add_node_item('FKIK Component', 'body.png', op_code=3)
        self.nodes_list.add_node_item('FK Component', 'body.png', op_code=4)
        self.nodes_list.add_node_item('IK Component', 'body.png', op_code=5)
        self.nodes_list.add_node_item('FKIK Spine Component', 'body.png', op_code=6)
        self.nodes_list.add_node_item('Hand Component', 'body.png', op_code=7)
        self.nodes_list.add_node_item('Foot Component', 'body.png', op_code=8)
        self.nodes_list.add_node_item('Eye Component', 'body.png', op_code=9)
        self.nodes_list.add_node_item('LipsComponent', 'body.png', op_code=10)
        self.nodes_list.add_node_item('IkStretch Component', 'body.png', op_code=11)
        self.nodes_list.add_node_item('Corrective Component', 'body.png', op_code=12)
        self.nodes_list.add_node_item('Ribbon Component', 'body.png', op_code=13)
        self.nodes_list.add_node_item('FK Dynamics Component', 'body.png', op_code=14)
        self.nodes_list.add_node_item('Wire Component', 'body.png', op_code=15)


class QLDragListBox(QtWidgets.QListWidget):

    PIXMAP_ROLE = QtCore.Qt.UserRole
    OP_CODE_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None):
        super(QLDragListBox, self).__init__(parent)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

    def add_node_item(self, label_text, icon_name=None, op_code=0):
        # Create icon
        if not icon_name:
            icon_name = os.path.join(directories.FALLBACK_IMG_PATH, 'noNodeIcon.png')
        else:
            icon_name = os.path.join(directories.ICONS_PATH, icon_name)
        pixmap = QtGui.QPixmap(icon_name)

        # Setup item
        item = QtWidgets.QListWidgetItem(label_text, self)
        item.setIcon(QtGui.QIcon(pixmap))
        item.setSizeHint(QtCore.QSize(32, 32))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
        # Setup data
        item.setData(QLDragListBox.PIXMAP_ROLE, pixmap)
        item.setData(QLDragListBox.OP_CODE_ROLE, op_code)

    def startDrag(self, event):
        Logger.debug('Palette::startDrag')
        try:
            item = self.currentItem()  # type: QtWidgets.QListWidgetItem
            op_code = item.data(QLDragListBox.OP_CODE_ROLE)
            pixmap = QtGui.QPixmap(item.data(QLDragListBox.PIXMAP_ROLE))

            # Pack item data
            item_data = QtCore.QByteArray()
            data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
            data_stream << pixmap
            data_stream.writeInt32(op_code)
            data_stream.writeQString(item.text())

            # Create mime data
            mime_data = QtCore.QMimeData()
            mime_data.setData(editor_conf.PALETTE_MIMETYPE, item_data)

            # Create drag
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
            drag.setPixmap(pixmap)

            Logger.debug('Dragging item <{0}>, {1}'.format(op_code, item))
            drag.exec_(QtCore.Qt.MoveAction)

        except Exception:
            Logger.exception('Palette drag exception')
