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

        # TODO: Replace with actual node items
        self.add_test_items()

    def create_widgets(self):
        self.nodes_tree = QLDragTreeWidget()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # self.main_layout.addWidget(self.nodes_list)
        self.main_layout.addWidget(self.nodes_tree)

    def create_connections(self):
        pass

    def add_test_items(self):
        for category in ['components', 'utils']:
            self.nodes_tree.add_category(category)

        self.nodes_tree.add_node_item('Character', category='components', icon_name='body.png', op_code=editor_conf.NODE_REGISTER.get('Character Component'))
        self.nodes_tree.add_node_item('Simple', category='components', icon_name='body.png', op_code=editor_conf.NODE_REGISTER.get('Simple Component'))
        self.nodes_tree.add_node_item('FKIK Component', category='components', icon_name='body.png', op_code=3)
        self.nodes_tree.add_node_item('FK Component', category='components', icon_name='body.png', op_code=4)
        self.nodes_tree.add_node_item('IK Component', category='components', icon_name='body.png', op_code=5)
        self.nodes_tree.add_node_item('FKIK Spine', category='components', icon_name='body.png', op_code=6)
        self.nodes_tree.add_node_item('Hand', category='components', icon_name='body.png', op_code=7)
        self.nodes_tree.add_node_item('Foot', category='components', icon_name='body.png', op_code=8)
        self.nodes_tree.add_node_item('Eye', category='components', icon_name='body.png', op_code=9)
        self.nodes_tree.add_node_item('Lips', category='components', icon_name='body.png', op_code=10)
        self.nodes_tree.add_node_item('IkStretch', category='components', icon_name='body.png', op_code=11)
        self.nodes_tree.add_node_item('Corrective', category='components', icon_name='body.png', op_code=12)
        self.nodes_tree.add_node_item('Ribbon', category='components', icon_name='body.png', op_code=13)
        self.nodes_tree.add_node_item('FK Dynamics', category='components', icon_name='body.png', op_code=14)
        self.nodes_tree.add_node_item('Wire Component', category='components', icon_name='body.png', op_code=15)


class QLDragTreeWidget(QtWidgets.QTreeWidget):

    PIXMAP_ROLE = QtCore.Qt.UserRole
    OP_CODE_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None):
        super(QLDragTreeWidget, self).__init__(parent)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

    def add_node_item(self, label_text, category='Undefiend', icon_name=None, op_code=0):
        if not icon_name:
            icon_name = os.path.join(directories.FALLBACK_IMG_PATH, 'noNodeIcon.png')
        else:
            icon_name = os.path.join(directories.ICONS_PATH, icon_name)
        pixmap = QtGui.QPixmap(icon_name)

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
        item.setData(0, QLDragTreeWidget.OP_CODE_ROLE, op_code)

    def add_category(self, name, expanded=True):
        tree_item = QtWidgets.QTreeWidgetItem(self)
        tree_item.setText(0, name.capitalize())
        tree_item.setExpanded(True)
        return tree_item

    def startDrag(self, event):
        Logger.debug('Palette::startDrag')
        try:
            item = self.currentItem()  # type: QtWidgets.QTreeWidgetItem
            op_code = item.data(0, QLDragTreeWidget.OP_CODE_ROLE)
            pixmap = QtGui.QPixmap(item.data(0, QLDragTreeWidget.PIXMAP_ROLE))

            # Pack item data
            item_data = QtCore.QByteArray()
            data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
            data_stream << pixmap
            data_stream.writeInt32(op_code)
            data_stream.writeQString(item.text(0))

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
