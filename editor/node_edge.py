import imp
from collections import OrderedDict

import luna.utils.enumFn as enumFn
import luna.utils.fileFn as fileFn
import luna_builder.editor.graphics_edge as graphics_edge
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_edge)


class Edge(node_serializable.Serializable):

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, scene, start_socket, end_socket):
        super(Edge, self).__init__()
        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket

        if self.start_socket is not None:
            self.start_socket.set_connected_edge(self)
        if self.end_socket is not None:
            self.end_socket.set_connected_edge(self)

        self.gr_edge = graphics_edge.QDGraphicsEdgeBezier(self)
        self.update_positions()
        self.scene.gr_scene.addItem(self.gr_edge)
        self.scene.add_edge(self)

    def update_positions(self):
        if self.start_socket:
            source_pos = self.start_socket.get_position()
            source_pos[0] += self.start_socket.node.gr_node.pos().x()
            source_pos[1] += self.start_socket.node.gr_node.pos().y()
            self.gr_edge.set_source(*source_pos)

        if self.end_socket:
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
        if self.start_socket is not None:
            self.start_socket.remove_edge(self)
        if self.end_socket is not None:
            self.end_socket.remove_edge(self)
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

    def deserialize(self, data, hashmap):
        pass
