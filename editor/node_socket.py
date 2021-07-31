import imp
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

        self.node = node
        self.index = index
        self.node_position = position if isinstance(position, Socket.Position) else Socket.Position(position)
        self.data_type = editor_conf.DataType.get_type(data_type) if isinstance(data_type, int) else data_type
        self._label = label if label else self.data_type.get('label')
        self.max_connections = max_connections
        self.count_on_this_side = count_on_this_side
        self._value = self.data_type.get('default') if value is None else value

        # Graphics
        self.gr_socket = graphics_socket.QLGraphicsSocket(self)
        self.update_positions()

        # Edge
        self.edges = []
        self.create_connections()

    def create_connections(self):
        pass

    # ===== Properties ===== #

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
        self._value = value
        self.signals.value_changed.emit()

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = editor_conf.DataType.get_type(value) if isinstance(value, int) else value
        if hasattr(self, 'gr_socket'):
            self.gr_socket._color_background = self._data_type.get('color')

    @property
    def data_class(self):
        return self.data_type.get('class')

    # ===== Methods ===== #
    def list_connections(self):
        result = []
        for edge in self.edges:
            for socket in [edge.start_socket, edge.end_socket]:
                if socket != self:
                    result.append(socket)
        return result

    def set_value(self, value):
        self.value = value

    def has_edge(self):
        return bool(self.edges)

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

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('position', self.node_position.value),
            ('data_type', self.data_type.get('index')),
            ('max_connections', self.max_connections),
            ('label', self.label),
            ('value', self.value)
        ])

    def deserialize(self, data, hashmap, restore_id=True):
        if restore_id:
            self.id = data.get('id')
        data_type = data['data_type']
        value = data.get('value', editor_conf.DataType.get_type(data_type)['default'])
        self.data_type = data['data_type']
        self.value = value
        hashmap[data['id']] = self
        return True


class InputSocket(Socket):

    def set_connected_edge(self, edge=None):
        super(InputSocket, self).set_connected_edge(edge=edge)
        if self.edges and edge not in self.edges:
            self.edges[0].remove()
        self.edges = [edge]

    def update_mathching_outputs(self):
        for output in self.node.outputs:
            if output.label.lower() == self.label.lower():
                output.value = self.value

    def create_connections(self):
        self.signals.value_changed.connect(self.update_mathching_outputs)


class OutputSocket(Socket):
    def create_connections(self):
        self.signals.value_changed.connect(self.update_connected_inputs)

    def set_connected_edge(self, edge=None):
        super(OutputSocket, self).set_connected_edge(edge=edge)
        if edge not in self.edges:
            self.edges.append(edge)

    def update_connected_inputs(self):
        for socket in self.list_connections():
            socket.value = self.value
