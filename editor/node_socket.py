import imp
from PySide2 import QtGui

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.graphics_socket as graphics_socket
imp.reload(graphics_socket)


class Socket(object):

    class Position(enumFn.Enum):
        LEFT_TOP = 1
        LEFT_BOTTOM = 2
        RIGHT_TOP = 3
        RIGHT_BOTTOM = 4

    # TODO: Class per socket type
    class DataType(enumFn.Enum):
        NUMERIC = 1
        STRING = 2
        COMPONENT = 3

    DATA_COLORS = {DataType.NUMERIC: QtGui.QColor("#FFFF7700"),
                   DataType.STRING: QtGui.QColor("#FF52e220"),
                   DataType.COMPONENT: QtGui.QColor("#FF0056a6")}

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, node, index=0, position=Position.LEFT_TOP, data_type=DataType.NUMERIC):
        self.node = node
        self.index = index
        self.posistion = position if isinstance(position, Socket.Position) else Socket.Position(position)
        self.data_type = data_type if isinstance(data_type, Socket.DataType) else Socket.DataType(data_type)

        # Graphics
        self.gr_socket = graphics_socket.QLGraphicsSocket(self, color=self.DATA_COLORS.get(self.data_type))
        self.gr_socket.setPos(*self.node.get_socket_position(self.index, self.posistion))

        # Edge
        self.edges = []

    def has_edge(self):
        return bool(self.edges)

    def get_position(self):
        return self.node.get_socket_position(self.index, self.posistion)

    def set_connected_edge(self, edge=None):
        if not edge:
            self.edges.clear()
            return

    def remove_edge(self, edge):
        if edge in self.edges:
            Logger.debug('Removing edge {0}'.format(edge))
            self.edges.remove(edge)


class InputSocket(Socket):
    def set_connected_edge(self, edge=None):
        super(InputSocket, self).set_connected_edge(edge=edge)
        if self.edges:
            self.edges[0].remove()
        self.edges = [edge]


class OutputSocket(Socket):
    def set_connected_edge(self, edge=None):
        super(OutputSocket, self).set_connected_edge(edge=edge)
        if edge not in self.edges:
            self.edges.append(edge)
