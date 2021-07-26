import os
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
import luna.utils.pysideFn as pysideFn
import luna.static.directories as directories


class NodesPalette(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(NodesPalette, self).__init__('Nodes Palette', parent)

        self.setMinimumWidth(150)

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
        self.nodes_list.add_node_item('Character Component', 'body.png')
        self.nodes_list.add_node_item('Simple Component', 'body.png')
        self.nodes_list.add_node_item('FKIK Component', 'body.png')
        self.nodes_list.add_node_item('FK Component', 'body.png')
        self.nodes_list.add_node_item('IK Component', 'body.png')
        self.nodes_list.add_node_item('FKIK Spine Component', 'body.png')
        self.nodes_list.add_node_item('Hand Component', 'body.png')
        self.nodes_list.add_node_item('Foot Component', 'body.png')
        self.nodes_list.add_node_item('Eye Component', 'body.png')
        self.nodes_list.add_node_item('LipsComponent', 'body.png')
        self.nodes_list.add_node_item('IkStretch Component', 'body.png')
        self.nodes_list.add_node_item('Corrective Component', 'body.png')
        self.nodes_list.add_node_item('Ribbon Component', 'body.png')
        self.nodes_list.add_node_item('FK Dynamics Component', 'body.png')
        self.nodes_list.add_node_item('Wire Component', 'body.png')


class QLDragListBox(QtWidgets.QListWidget):
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
        item.setData(QtCore.Qt.UserRole, pixmap)
        item.setData(QtCore.Qt.UserRole + 1, op_code)
