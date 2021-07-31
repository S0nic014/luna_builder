from PySide2 import QtWidgets
from collections import OrderedDict

from luna import Logger
import luna_builder.editor.node_node as node_node
import luna_builder.editor.editor_conf as editor_conf


class AttribWidget(QtWidgets.QWidget):
    def __init__(self, node, parent=None):
        super(AttribWidget, self).__init__(parent)
        self.node = node
        self.fields_map = OrderedDict()

        self.main_layout = QtWidgets.QFormLayout()
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.init_fields()

    def showEvent(self, event):
        super(AttribWidget, self).showEvent(event)
        self.update_fields()

    def init_fields(self):
        self.fields_map.clear()
        IGNORED_DATA_TYPES = [editor_conf.DataType.EXEC, editor_conf.DataType.LIST]
        IGNORED_CLASSES = [dt['class'] for dt in IGNORED_DATA_TYPES]
        for socket in self.node.inputs:
            try:
                if any([issubclass(socket.data_class, dt_class) for dt_class in IGNORED_CLASSES]):
                    continue

                widget = None
                if issubclass(socket.data_class, editor_conf.DataType.STRING.get('class')):
                    widget = QtWidgets.QLineEdit()
                elif issubclass(socket.data_class, editor_conf.DataType.NUMERIC.get('class')):
                    widget = QtWidgets.QDoubleSpinBox()
                elif issubclass(socket.data_class, editor_conf.DataType.BOOLEAN.get('class')):
                    widget = QtWidgets.QCheckBox()
                # elif issubclass(socket.data_class, editor_conf.DataType.LIST.get('class')):
                #     widget = QtWidgets.QListWidget()
                elif issubclass(socket.data_class, editor_conf.DataType.PYNODE.get('class')):
                    widget = QtWidgets.QLineEdit()
                elif issubclass(socket.data_class, editor_conf.DataType.CONTROL.get('class')):
                    widget = QtWidgets.QLineEdit()
                elif issubclass(socket.data_class, editor_conf.DataType.COMPONENT.get('class')):
                    widget = QtWidgets.QLineEdit()
                else:
                    Logger.error('Failed to create attribute field: {0}::{1}'.format(socket, socket.data_class))
                if widget:
                    # Store in the map and add to layout
                    self.fields_map[socket.label] = (socket, widget)
                    self.main_layout.addRow(socket.label, widget)
                # Signals
            except Exception:
                Logger.exception('Attribute field add exception')

        self.update_fields()
        self.update_signal_connections()

    def update_signal_connections(self):
        for label, socket_widget_pair in self.fields_map.items():
            socket, widget = socket_widget_pair
            if isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(socket.set_value)
            elif isinstance(widget, QtWidgets.QAbstractSpinBox):
                widget.valueChanged.connect(socket.set_value)
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.toggled.connect(socket.set_value)

    def update_widget_value(self, socket, widget):
        if issubclass(socket.data_class, editor_conf.DataType.STRING.get('class')):
            widget.setText(socket.value)
        elif issubclass(socket.data_class, editor_conf.DataType.NUMERIC.get('class')):
            if socket.value:
                widget.setValue(socket.value)
        elif issubclass(socket.data_class, editor_conf.DataType.BOOLEAN.get('class')):
            widget.setChecked(socket.value)
        # elif issubclass(socket.data_class, editor_conf.DataType.LIST.get('class')):
        elif issubclass(socket.data_class, editor_conf.DataType.PYNODE.get('class')):
            widget.setText(str(socket.value))
        elif issubclass(socket.data_class, editor_conf.DataType.CONTROL.get('class')):
            if socket.value:
                widget.setText(str(socket.value.transform))
            else:
                widget.clear()
        elif issubclass(socket.data_class, editor_conf.DataType.COMPONENT.get('class')):
            if socket.value:
                widget.setText(str(socket.value.pynode))
        else:
            Logger.error('Failed to create attribute field: {0}::{1}'.format(socket, socket.data_class))

    def update_fields(self):
        self.blockSignals(True)
        for label, socket_widget_pair in self.fields_map.items():
            socket, widget = socket_widget_pair
            widget.setEnabled(not socket.has_edge())
            self.update_widget_value(socket, widget)
        self.blockSignals(False)


class LunaNode(node_node.Node):

    ID = None
    ICON = None
    DEFAULT_TITLE = 'Luna Node'
    UNIQUE = False
    CATEGORY = 'Utils'
    INSPECTOR_WIDGET = AttribWidget

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(LunaNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    def pre_deserilization(self, data):
        pass

    def post_deserilization(self, data):
        pass

    def serialize(self):
        data_dict = super(LunaNode, self).serialize()
        data_dict['node_id'] = self.__class__.ID
        return data_dict

    def deserialize(self, data, hashmap, restore_id):
        self.pre_deserilization(data)
        super(LunaNode, self).deserialize(data, hashmap=hashmap, restore_id=restore_id)
        self.post_deserilization(data)

    def execute(self):
        pass
