import os
import json
import pymel.core as pm
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
import luna.static.directories as directories
import luna_builder.editor.editor_conf as editor_conf


class NodesPalette(QtWidgets.QWidget):
    def __init__(self, parent=None, icon_size=32, data_type_filter=None, functions_first=False):
        super(NodesPalette, self).__init__(parent)

        self.icon_size = QtCore.QSize(icon_size, icon_size)
        self.data_type_filter = data_type_filter
        self._functions_first = functions_first

        self.setMinimumWidth(190)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.update_node_tree()

    @property
    def functions_first(self):
        return self._functions_first

    @functions_first.setter
    def functions_first(self, state):
        self._functions_first = state
        self.update_node_tree()

    def create_widgets(self):
        self.completer = QtWidgets.QCompleter()
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setModelSorting(QtWidgets.QCompleter.CaseInsensitivelySortedModel)

        self.search_line = QtWidgets.QLineEdit()
        self.search_line.setPlaceholderText('Search')
        self.search_line.setCompleter(self.completer)
        self.nodes_tree = QLDragTreeWidget(self)
        # self.nodes_tree.setModel(self.completer.completionModel())

    def create_model(self):

        all_items = self.nodes_tree.findItems("*", QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive)
        item_labels = [item.text(0) for item in all_items]
        # item_labels.sort(key=str.lower)
        if int(pm.about(v=1)) < 2020:
            self.completer.setModel(QtGui.QStringListModel(item_labels))
        else:
            self.completer.setModel(QtCore.QStringListModel(item_labels))

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.search_line)
        self.main_layout.addWidget(self.nodes_tree)

    def create_connections(self):
        self.search_line.textChanged.connect(self.completer.setCompletionPrefix)

    def update_node_tree(self):
        self.nodes_tree.populate()
        self.create_model()


class QLDragTreeWidget(QtWidgets.QTreeWidget):

    PIXMAP_ROLE = QtCore.Qt.UserRole
    NODE_ID_ROLE = QtCore.Qt.UserRole + 1
    JSON_DATA_ROLE = QtCore.Qt.UserRole + 2

    def __init__(self, nodes_palette, parent=None):
        super(QLDragTreeWidget, self).__init__(parent)
        self.nodes_palette = nodes_palette

        self.setIconSize(self.nodes_palette.icon_size)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

    def add_node_item(self, node_id, label_text, func_signature='', category='Undefiend', icon_name=None, expanded=True):
        if not icon_name:
            icon_name = 'func.png'
        icon_path = os.path.join(directories.ICONS_PATH, icon_name)
        pixmap = QtGui.QPixmap(icon_path)

        # Find parent
        category_path = category.split('/')
        parent_item = self
        for category_name in category_path:
            parent_item = self.get_category(category_name, parent=parent_item, expanded=expanded)

        # Setup item
        item = QtWidgets.QTreeWidgetItem()
        parent_item.addChild(item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
        item.setText(0, label_text)
        item.setIcon(0, QtGui.QIcon(pixmap))
        item.setSizeHint(0, self.nodes_palette.icon_size)
        # Setup item
        item.setData(0, QLDragTreeWidget.PIXMAP_ROLE, pixmap)
        item.setData(0, QLDragTreeWidget.NODE_ID_ROLE, node_id)
        json_data = {
            'title': item.text(0),
            'func_signature': func_signature
        }

        item.setData(0, QLDragTreeWidget.JSON_DATA_ROLE, json_data)
        return item

    def add_category(self, name, expanded=True, parent=None):
        if not parent:
            parent = self
        tree_item = QtWidgets.QTreeWidgetItem(parent)
        tree_item.setText(0, name)
        tree_item.setExpanded(expanded)
        return tree_item

    def get_category(self, name, expanded=True, parent=None):
        found_items = self.findItems(name, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
        if parent is not self:
            found_items = [item for item in found_items if item.parent() is parent]
        item = found_items[0] if found_items else self.add_category(name, expanded=expanded, parent=parent)
        return item

    def startDrag(self, event):
        Logger.debug('Palette::startDrag')
        try:
            item = self.currentItem()  # type: QtWidgets.QTreeWidgetItem
            node_id = item.data(0, QLDragTreeWidget.NODE_ID_ROLE)
            pixmap = QtGui.QPixmap(item.data(0, QLDragTreeWidget.PIXMAP_ROLE))

            # Pack data to json
            json_data = item.data(0, QLDragTreeWidget.JSON_DATA_ROLE)

            # Pack data to data stream
            item_data = QtCore.QByteArray()
            data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
            data_stream << pixmap
            data_stream.writeInt32(node_id)
            data_stream.writeQString(json.dumps(json_data))

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

    def populate(self):
        self.clear()
        if self.nodes_palette.functions_first:
            self.add_registered_functions()
            self.add_registered_nodes()
        else:
            self.add_registered_nodes()
            self.add_registered_functions()

    def add_registered_nodes(self):
        keys = list(editor_conf.NODE_REGISTER.keys())
        keys.sort()
        for node_id in keys:
            node_class = editor_conf.NODE_REGISTER[node_id]
            if node_class.CATEGORY == editor_conf.INTERNAL_CATEGORY:
                continue
            palette_label = node_class.PALETTE_LABEL if hasattr(node_class, 'PALETTE_LABEL') else node_class.DEFAULT_TITLE
            self.add_node_item(node_id, palette_label, category=node_class.CATEGORY, icon_name=node_class.ICON)

    def add_registered_functions(self):
        keys = list(editor_conf.FUNCTION_REGISTER.keys())
        keys.sort()
        for datatype_name in keys:
            if datatype_name != editor_conf.UNBOUND_FUNCTION_DATATYPE and self.nodes_palette.data_type_filter:
                if not issubclass(self.nodes_palette.data_type_filter.get('class'), editor_conf.DataType.get_type(datatype_name).get('class')):
                    continue
            func_map = editor_conf.FUNCTION_REGISTER[datatype_name]
            func_signatures_list = func_map.keys()
            func_signatures_list = list(func_signatures_list) if not isinstance(func_signatures_list, list) else func_signatures_list
            for func_sign in func_signatures_list:
                if datatype_name != editor_conf.UNBOUND_FUNCTION_DATATYPE:
                    expanded = self.nodes_palette.functions_first
                else:
                    expanded = True
                func_dict = func_map[func_sign]
                icon_name = func_dict['icon']
                nice_name = func_dict.get('nice_name')
                sub_category_name = func_dict.get('category', 'General')
                palette_name = nice_name if nice_name else func_sign

                self.add_node_item(editor_conf.FUNC_NODE_ID,
                                   palette_name,
                                   func_signature=func_sign,
                                   category='Functions/{0}'.format(sub_category_name),
                                   icon_name=icon_name,
                                   expanded=expanded)
