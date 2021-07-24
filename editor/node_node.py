import imp
from collections import OrderedDict

from luna import Logger
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_node)
imp.reload(node_socket)


class Node(node_serializable.Serializable):

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, scene, title="Custom node", inputs=[], outputs=[]):
        super(Node, self).__init__()
        self._title = title
        self.scene = scene

        # Setup graphics
        self.gr_node = graphics_node.QLGraphicsNode(self)
        self.title = title

        # Add to the scene
        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)

        # Create sockets
        self.socket_spacing = 22
        self.inputs = []
        self.outputs = []
        self.exec_in_socket = node_socket.InputSocket(self,
                                                      index=0,
                                                      position=node_socket.Socket.Position.LEFT_TOP,
                                                      data_type=node_socket.Socket.DataType.EXEC,
                                                      label='',
                                                      max_connections=1)
        self.inputs.append(self.exec_in_socket)

        self.exec_out_socket = node_socket.OutputSocket(self,
                                                        index=0,
                                                        position=node_socket.Socket.Position.RIGHT_TOP,
                                                        data_type=node_socket.Socket.DataType.EXEC,
                                                        label='',
                                                        max_connections=1)
        self.outputs.append(self.exec_out_socket)

        # TODO: Probably turn into method
        for index, item in enumerate(inputs):
            socket = node_socket.InputSocket(node=self,
                                             index=index + 1,
                                             position=node_socket.Socket.Position.LEFT_TOP,
                                             data_type=item,
                                             label='input{0}'.format(index))
            self.inputs.append(socket)

        for index, item in enumerate(outputs):
            socket = node_socket.OutputSocket(node=self,
                                              index=index + 1,
                                              position=node_socket.Socket.Position.RIGHT_TOP,
                                              data_type=item,
                                              label='output{0}'.format(index))
            self.outputs.append(socket)

    @property
    def position(self):
        return self.gr_node.pos()

    def set_position(self, x, y):
        self.gr_node.setPos(x, y)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.gr_node.title = self._title

    def get_socket_position(self, index, position):
        # TODO: Resize node if Y coordiante goes beyond node height
        if position in (node_socket.Socket.Position.LEFT_TOP, node_socket.Socket.Position.LEFT_BOTTOM):
            x = 0
        else:
            x = self.gr_node.width

        if position in (node_socket.Socket.Position.LEFT_BOTTOM, node_socket.Socket.Position.RIGHT_BOTTOM):
            # start from top
            y = self.gr_node.height - self.gr_node.edge_size - self.gr_node._padding - index * self.socket_spacing
        else:
            # start from bottom
            y = self.gr_node.title_height + self.gr_node._padding + self.gr_node.edge_size + index * self.socket_spacing

        return [x, y]

    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            socket.update_edges()

    def remove(self):
        try:
            for socket in self.inputs + self.outputs:
                for edge in socket.edges:
                    edge.remove()
            self.scene.gr_scene.removeItem(self.gr_node)
            self.gr_node = None
            self.scene.remove_node(self)
        except Exception:
            Logger.exception('Failed to delete node {0}'.format(self))

    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs:
            inputs.append(socket.serialize())
        for socket in self.outputs:
            outputs.append(socket.serialize())

        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.gr_node.scenePos().x()),
            ('pos_y', self.gr_node.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs)
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data.get('id')
        hashmap[data['id']] = self

        self.set_position(data['pos_x'], data['pos_y'])
        self.title = data.get('title')

        # Sockets
        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)

        self.inputs = []
        self.outputs = []
        for socket_data in data.get('inputs'):
            new_socket = node_socket.InputSocket(self,
                                                 index=socket_data['index'],
                                                 position=socket_data['position'],
                                                 data_type=socket_data['data_type'],
                                                 label=socket_data['label'],
                                                 max_connections=socket_data['max_connections'])
            new_socket.deserialize(socket_data, hashmap)
            self.inputs.append(new_socket)

        for socket_data in data.get('outputs'):
            new_socket = node_socket.OutputSocket(self,
                                                  index=socket_data['index'],
                                                  position=socket_data['position'],
                                                  data_type=socket_data['data_type'],
                                                  label=socket_data['label'],
                                                  max_connections=socket_data['max_connections'])
            new_socket.deserialize(socket_data, hashmap)
            self.outputs.append(new_socket)
