import imp
from PySide2 import QtGui
from collections import OrderedDict

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.graphics_socket as graphics_socket
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_socket)


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
        self.set_position()

        # Edge
        self.edges = []

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

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = editor_conf.DataType.get_type(value) if isinstance(value, int) else value
        if hasattr(self, 'gr_socket'):
            self.gr_socket._color_background = self._data_type.get('color')

    # ===== Methods ===== #

    def has_edge(self):
        return bool(self.edges)

    def set_position(self):
        self.gr_socket.setPos(*self.node.get_socket_position(self.index, self.node_position, self.count_on_this_side))
        self.gr_socket.text_item.setPos(*self.get_label_position(self.gr_socket.text_item))

    def get_position(self):
        return self.node.get_socket_position(self.index, self.node_position, self.count_on_this_side)

    def get_label_position(self, text_item):
        text_width = text_item.boundingRect().width()
        if self.node_position in [Socket.Position.LEFT_TOP, Socket.Position.LEFT_BOTTOM]:
            return [self.node.gr_node.width / 25.0, Socket.LABEL_VERTICAL_PADDING]
        else:
            clamped_x = -(self.node.gr_node.width / 2 + text_width) * 0.55
            return [clamped_x, Socket.LABEL_VERTICAL_PADDING]

    def get_label_width(self):
        if self.node_position in [Socket.Position.LEFT_TOP, Socket.Position.LEFT_BOTTOM]:
            return self.node.gr_node.width * 0.45
        else:
            return self.node.gr_node.width / 2 * 0.8

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
        hashmap[data['id']] = self


class InputSocket(Socket):

    def set_connected_edge(self, edge=None):
        super(InputSocket, self).set_connected_edge(edge=edge)
        if self.edges and edge not in self.edges:
            self.edges[0].remove()
        self.edges = [edge]


class OutputSocket(Socket):
    def set_connected_edge(self, edge=None):
        super(OutputSocket, self).set_connected_edge(edge=edge)
        if edge not in self.edges:
            self.edges.append(edge)
