import imp
import pymel.core as pm
from PySide2 import QtCore
from collections import OrderedDict

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.graphics_socket as graphics_socket
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_socket)


class SocketSignals(QtCore.QObject):
    value_changed = QtCore.Signal()
    connection_changed = QtCore.Signal()


class Socket(node_serializable.Serializable):

    class Position(enumFn.Enum):
        LEFT_TOP = 1
        LEFT_CENTER = 2
        LEFT_BOTTOM = 3
        RIGHT_TOP = 4
        RIGHT_CENTER = 5
        RIGHT_BOTTOM = 6

    LABEL_VERTICAL_PADDING = -10.0

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self,
                 node,
                 index=0,
                 position=Position.LEFT_TOP,
                 data_type=editor_conf.DataType.NUMERIC,
                 label=None,
                 max_connections=0,
                 value=None,
                 count_on_this_side=0):
        super(Socket, self).__init__()
        self.signals = SocketSignals()
        self.edges = []

        self.node = node
        self.index = index
        self.node_position = position if isinstance(position, Socket.Position) else Socket.Position(position)
        # self.data_type = editor_conf.DataType.get_type(data_type) if isinstance(data_type, int) else data_type
        self.data_type = data_type
        self._label = label if label else self.data_type.get('label')
        self.max_connections = max_connections
        self.count_on_this_side = count_on_this_side
        self._value = self.data_type.get('default') if value is None else value
        self._default_value = self.value

        # Graphics
        self.gr_socket = graphics_socket.QLGraphicsSocket(self)
        self.update_positions()

        # Signals
        self.create_connections()

    def create_connections(self):
        pass

    # ============ Properties ============= #

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, text):
        self._label = text
        self.gr_socket.text_item.setPlainText(self._label)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.data_type == editor_conf.DataType.EXEC:
            return
        if self._value == value:
            return
        if isinstance(value, pm.PyNode):
            value = str(value)

        self._value = value
        self.signals.value_changed.emit()

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        if isinstance(value, str):
            self._data_type = editor_conf.DATATYPE_REGISTER[value]
        elif isinstance(value, dict):
            self._data_type = value
        else:
            Logger.error('{0}: Can\'t set datatype to {0}'.format(value))
            raise ValueError
        if hasattr(self, 'gr_socket'):
            self.gr_socket._color_background = self._data_type.get('color')
            self.gr_socket.update()
        # Remove not valid connections
        for edge in self.edges:
            if not self.can_be_connected(edge.get_other_socket(self)):
                edge.remove()

    @ property
    def data_class(self):
        return self.data_type.get('class')

    # ============ Basic methods ============= #
    def remove(self):
        self.remove_all_edges()
        self.node.scene.gr_scene.removeItem(self.gr_socket)

    # ============ Datatype methods ============= #

    def is_runtime_data(self):
        # return any([issubclass(self.data_class, dt['class']) for dt in editor_conf.DataType.runtime_types()])
        return self.data_class in editor_conf.DataType.runtime_types(classes=True)
    # ============ Value methods ============= #

    def set_value(self, value):
        self.value = value

    def reset_value_to_default(self):
        self.value = self.default_value

    # ============ Graphics objects methods ============= #

    def update_positions(self):
        self.gr_socket.setPos(*self.node.get_socket_position(self.index, self.node_position, self.count_on_this_side))
        self.gr_socket.text_item.setPos(*self.get_label_position())

    def get_position(self):
        return self.node.get_socket_position(self.index, self.node_position, self.count_on_this_side)

    def get_label_position(self):
        text_width = self.gr_socket.text_item.boundingRect().width()
        if self.node_position in [Socket.Position.LEFT_TOP, Socket.Position.LEFT_BOTTOM]:
            return [self.node.gr_node.width / 25.0, Socket.LABEL_VERTICAL_PADDING]
        else:
            return [-text_width - self.node.gr_node.width / 25, Socket.LABEL_VERTICAL_PADDING]

    def get_label_width(self):
        return self.gr_socket.text_item.boundingRect().width()

    # ============ Edge Methods ============= #

    def has_edge(self):
        return bool(self.edges)

    def set_connected_edge(self, edge=None):
        if not edge:
            self.edges.clear()
            return
        if self.edges and self.max_connections and len(self.edges) > self.max_connections:
            self.edges[0].remove()

    def remove_all_edges(self):
        while self.edges:
            self.edges[0].remove()
        self.edges = []

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def update_edges(self):
        for edge in self.edges:
            edge.update_positions()

    # ============ Connections methods ============= #
    def can_be_connected(self, other_socket):
        # Clicking on socket edge is dragging from
        if self is other_socket:
            return False

        # Trying to connect output->output or input->input
        if isinstance(other_socket, self.__class__):
            Logger.warning('Can\'t connect two sockets of the same type')
            return False

        if self.node is other_socket.node:
            Logger.warning('Can\'t connect sockets on the same node')
            return False

        #!FIX: Find a way to check for cycles
        # if assigned_socket.node in item.socket.node.list_children(recursive=True) or item.socket.node in assigned_socket.node.list_children():
        #     Logger.warning('Can\'t create connection due to cycle')
        #     return False

        return True

    def list_connections(self):
        result = []
        for edge in self.edges:
            for socket in [edge.start_socket, edge.end_socket]:
                if socket and socket != self:
                    result.append(socket)
        return result

    # ============ (De)Serialization ============= #
    def serialize(self):
        if self.is_runtime_data():
            value = None
        else:
            value = self.value

        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('position', self.node_position.value),
            ('data_type', editor_conf.DataType.get_type_name(self.data_type)),
            ('max_connections', self.max_connections),
            ('label', self.label),
            ('value', value)
        ])

    def deserialize(self, data, hashmap, restore_id=True):
        if restore_id:
            self.id = data.get('id')
        data_type = editor_conf.DataType.get_type(data['data_type'])
        value = data.get('value', data_type['default'])
        self.data_type = data_type
        self.value = value
        hashmap[data['id']] = self
        return True


class InputSocket(Socket):
    def create_connections(self):
        self.signals.connection_changed.connect(self.on_connection_changed)
        self.signals.value_changed.connect(self.update_matching_outputs)
        self.signals.value_changed.connect(self.node.set_compiled)

    def on_connection_changed(self):
        if not self.has_edge() and self.is_runtime_data():
            self.value = self.data_type['default']

    def can_be_connected(self, other_socket):
        super(InputSocket, self).can_be_connected(other_socket)
        if not issubclass(other_socket.data_class, self.data_class):
            Logger.warning('Can\'t connect data types {0} and {1}'.format(other_socket.data_class, self.data_class))
            return False
        return True

    def set_connected_edge(self, edge=None):
        super(InputSocket, self).set_connected_edge(edge=edge)
        if self.edges and edge not in self.edges:
            self.edges[0].remove()
        self.edges = [edge]
        self.signals.connection_changed.emit()

    def update_matching_outputs(self):
        for output in self.node.outputs:
            if output.label.lower() == self.label.lower():
                output.value = self.value


class OutputSocket(Socket):
    def create_connections(self):
        self.signals.value_changed.connect(self.update_connected_inputs)

    def can_be_connected(self, other_socket):
        super(OutputSocket, self).can_be_connected(other_socket)
        if not issubclass(self.data_class, other_socket.data_class):
            Logger.warning('Can\'t connect data types {0} and {1}'.format(other_socket.data_class, self.data_class))
            return False
        return True

    def set_connected_edge(self, edge=None):
        super(OutputSocket, self).set_connected_edge(edge=edge)
        if edge not in self.edges:
            self.edges.append(edge)

    def update_connected_inputs(self):
        for socket in self.list_connections():
            socket.value = self.value
