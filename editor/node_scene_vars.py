import json
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.node_serializable as node_serializable


class VarsSignals(QtCore.QObject):
    value_changed = QtCore.Signal(str)


class SceneVars(node_serializable.Serializable):
    def __init__(self, scene):
        super(SceneVars, self).__init__()
        self.scene = scene
        self.signals = VarsSignals()
        self._vars = {'test': (2.0, editor_conf.DataType.NUMERIC)}
        self.create_connections()

    def create_connections(self):
        self.signals.value_changed.connect(self.update_getters)

    def set_var(self, name, value, datatype):
        self._vars[name] = (value, datatype)
        self.signals.value_changed.emit(name)

    def update_getters(self, var_name):
        Logger.debug('Updating getters...')
        for getter_node in {node for node in self.scene.nodes if node.ID == editor_conf.GET_NODE_ID and node.var_name == var_name}:
            Logger.debug('   > Updating {0}'.format(getter_node))
            if not getter_node.out_value.data_type == self.get_data_type(var_name):
                getter_node.out_value.data_type = self.get_data_type(var_name)

            getter_node.out_value.value = self.get_value(var_name)

    def get_value(self, name):
        return self._vars[name][0]

    def get_data_type(self, name):
        return self._vars[name][1]

    def serialize(self):
        return {}

    def deserialize(self, data, hashmap={}):
        super(SceneVars, self).deserialize(data, hashmap=hashmap)


class SceneVarsWidget(QtWidgets.QGroupBox):
    def __init__(self, main_dialog, parent=None):
        super(SceneVarsWidget, self).__init__(parent)
        self.main_dialog = main_dialog
        self.setTitle('Variables')
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    @property
    def scene_vars(self):
        if not self.main_dialog.current_editor:
            return None
        return self.main_dialog.current_editor.scene.vars

    def create_widgets(self):
        self.var_list = QLVarsListWidget(self)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.var_list)

    def create_connections(self):
        pass

    def update_var_list(self):
        self.var_list.populate(self.scene_vars)


class QLVarsListWidget(QtWidgets.QListWidget):

    PIXMAP_ROLE = QtCore.Qt.UserRole
    JSON_DATA_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, vars_widget, parent=None):
        super(QLVarsListWidget, self).__init__(parent)
        self.vars_widget = vars_widget

        # self.setIconSize(self.nodes_palette.icon_size)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

    def populate(self, scene_vars):
        self.clear()
        if not scene_vars:
            Logger.error('Failed to populate Vars list, scene_vars is {0}'.format(scene_vars))
            return

        for var_name, value_dt_pair in scene_vars._vars.items():
            new_item = QtWidgets.QListWidgetItem()
            self.addItem(new_item)
            new_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
            new_item.setText(var_name)
            # new_item.setIcon()
            # new_item.setSizeHint()
            json_data = {'var_name': var_name}
            new_item.setData(QLVarsListWidget.JSON_DATA_ROLE, json_data)

    def startDrag(self, event):
        Logger.debug('Vars::startDrag')
        try:
            item = self.currentItem()  # type: QtWidgets.QTreeWidgetItem

            # Pack data to json
            json_data = item.data(QLVarsListWidget.JSON_DATA_ROLE)

            # Pack data to data stream
            item_data = QtCore.QByteArray()
            data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
            data_stream.writeQString(json.dumps(json_data))

            # Create mime data
            mime_data = QtCore.QMimeData()
            mime_data.setData(editor_conf.VARS_MIMETYPE, item_data)

            # Create drag
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            # drag.setHotSpot(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
            # drag.setPixmap(pixmap)

            Logger.debug('Dragging item <{0}>'.format(item.text()))
            drag.exec_(QtCore.Qt.MoveAction)

        except Exception:
            Logger.exception('Vars drag exception')
