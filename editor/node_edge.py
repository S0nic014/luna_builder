import imp
from collections import OrderedDict

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.graphics_edge as graphics_edge
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_edge)


class Edge(node_serializable.Serializable):

    class Type(enumFn.Enum):
        DIRECT = 1
        BEZIER = 2

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, scene, start_socket=None, end_socket=None):
        super(Edge, self).__init__()
        self._start_socket = None
        self._end_socket = None
        self.scene = scene

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.update_edge_graphics_type()
        self.scene.add_edge(self)

    @property
    def start_socket(self):
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        if self._start_socket is not None:
            self._start_socket.remove_edge(self)

        self._start_socket = value
        if self._start_socket is not None:
            self._start_socket.set_connected_edge(self)

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        if self._end_socket is not None:
            self._end_socket.remove_edge(self)

        self._end_socket = value
        if self._end_socket is not None:
            self._end_socket.set_connected_edge(self)

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'gr_edge') and self.gr_edge is not None:
            self.scene.gr_scene.removeItem(self.gr_edge)
        self._edge_type = value if isinstance(value, Edge.Type) else Edge.Type(value)
        if self._edge_type == Edge.Type.DIRECT:
            self.gr_edge = graphics_edge.QLGraphicsEdgeDirect(self)
        elif self._edge_type == Edge.Type.BEZIER:
            self.gr_edge = graphics_edge.QDGraphicsEdgeBezier(self)
        else:
            self.gr_edge = graphics_edge.QDGraphicsEdgeBezier(self)
        self.scene.gr_scene.addItem(self.gr_edge)
        if self.start_socket or self.end_socket:
            self.update_positions()

    def update_edge_graphics_type(self):
        self.edge_type = self.scene.edge_type

    def update_positions(self):
        if self.start_socket is not None:
            source_pos = self.start_socket.get_position()
            source_pos[0] += self.start_socket.node.gr_node.pos().x()
            source_pos[1] += self.start_socket.node.gr_node.pos().y()
            self.gr_edge.set_source(*source_pos)

        if self.end_socket is not None:
            end_pos = self.end_socket.get_position()
            end_pos[0] += self.end_socket.node.gr_node.pos().x()
            end_pos[1] += self.end_socket.node.gr_node.pos().y()
            self.gr_edge.set_destination(*end_pos)

        if not self.start_socket:
            self.gr_edge.set_source(*end_pos)
        if not self.end_socket:
            self.gr_edge.set_destination(*source_pos)
        self.gr_edge.update()

    def remove_from_sockets(self):
        self.start_socket = None
        self.end_socket = None

    def remove(self):
        self.remove_from_sockets()
        self.scene.gr_scene.removeItem(self.gr_edge)
        self.gr_edge = None
        self.scene.remove_edge(self)

    def get_assigned_socket(self):
        if self.start_socket and self.end_socket:
            return (self.start_socket, self.end_socket)
        elif not self.end_socket:
            return self.start_socket
        else:
            return self.end_socket

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id)
        ])

    def deserialize(self, data, hashmap, restore_id=True):
        if restore_id:
            self.id = data.get('id')
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.update_edge_graphics_type()
