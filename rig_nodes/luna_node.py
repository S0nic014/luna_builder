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

    def init_fields(self):
        IGNORED_DATA_TYPES = [editor_conf.DataType.EXEC, editor_conf.DataType.LIST]
        IGNORED_CLASSES = [dt['class'] for dt in IGNORED_DATA_TYPES]
        for socket in self.node.inputs:
            try:
                if any([issubclass(socket.data_class, dt_class) for dt_class in IGNORED_CLASSES]):
                    continue

                widget = None
                if issubclass(socket.data_class, editor_conf.DataType.STRING.get('class')):
                    widget = QtWidgets.QLineEdit()
                    widget.setText(socket.value)
                elif issubclass(socket.data_class, editor_conf.DataType.NUMERIC.get('class')):
                    widget = QtWidgets.QDoubleSpinBox()
                    if socket.value:
                        widget.setValue(socket.value)
                elif issubclass(socket.data_class, editor_conf.DataType.BOOLEAN.get('class')):
                    widget = QtWidgets.QCheckBox()
                    widget.setChecked(socket.value)
                # elif issubclass(socket.data_class, editor_conf.DataType.LIST.get('class')):
                #     widget = QtWidgets.QListWidget()
                elif issubclass(socket.data_class, editor_conf.DataType.PYNODE.get('class')):
                    widget = QtWidgets.QLineEdit()
                    widget.setText(str(socket.value))
                elif issubclass(socket.data_class, editor_conf.DataType.CONTROL.get('class')):
                    widget = QtWidgets.QLineEdit()
                    if socket.value:
                        widget.setText(str(socket.value.transform))
                    else:
                        widget.clear()
                elif issubclass(socket.data_class, editor_conf.DataType.COMPONENT.get('class')):
                    widget = QtWidgets.QLineEdit()
                    if socket.value:
                        widget.setText(str(socket.value.pynode))
                else:
                    Logger.error('Failed to create attribute field: {0}::{1}'.format(socket, socket.data_class))
                if widget:
                    self.fields_map[socket.label] = (socket, widget)
                    self.main_layout.addRow(socket.label, widget)
                    if isinstance(widget, QtWidgets.QLineEdit):
                        widget.textChanged.connect(socket.set_value)
                    elif isinstance(widget, QtWidgets.QAbstractSpinBox):
                        widget.valueChanged.connect(socket.set_value)
                    elif isinstance(widget, QtWidgets.QCheckBox):
                        widget.toggled.connect(socket.set_value)

            except Exception:
                Logger.exception('Attribute field add exception')


class LunaNode(node_node.Node):

    ID = None
    ICON = None
    DEFAULT_TITLE = 'Luna Node'
    UNIQUE = False
    CATEGORY = 'Utils'
    INSPECTOR_WIDGET = AttribWidget

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(LunaNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)
        self.attrib_widget = AttribWidget(self)

    def serialize(self):
        data_dict = super(LunaNode, self).serialize()
        data_dict['node_id'] = self.__class__.ID
        return data_dict

    def execute(self):
        pass
