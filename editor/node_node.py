import imp
from collections import OrderedDict

from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_node)
imp.reload(node_socket)


class Node(node_serializable.Serializable):

    SIZE = (180, 240)
    TITLE_HEIGHT = 24

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, scene, title="Custom node", inputs=[], outputs=[]):
        super(Node, self).__init__()
        self.scene = scene
        self.socket_spacing = 22
        self._title = title

        # Setup graphics
        self.gr_node = graphics_node.QLGraphicsNode(self)

        # Add to the scene
        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)

        # Create sockets
        self.inputs = []
        self.outputs = []

        # EXEC sockets
        self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
        self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC, max_connections=1)

        # Test sockets
        # TODO: Remove after tests
        for index, item in enumerate(inputs):
            self.add_input(item, None, None)

        for index, item in enumerate(outputs):
            self.add_output(item, None, None)

    # ======= Properties ======= #
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

    # ======= Methods ======= #

    def get_new_input_index(self):
        return len(self.inputs)

    def get_new_output_index(self):
        return len(self.outputs)

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
                socket.remove_all_edges()
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

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
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
            data_type = socket_data['data_type']
            new_socket = node_socket.InputSocket(self,
                                                 index=socket_data['index'],
                                                 position=socket_data['position'],
                                                 data_type=data_type,
                                                 label=socket_data['label'],
                                                 max_connections=socket_data['max_connections'],
                                                 value=socket_data.get('value', editor_conf.DataType.get_type(data_type)['default']))
            new_socket.deserialize(socket_data, hashmap, restore_id=restore_id)
            self.inputs.append(new_socket)

        for socket_data in data.get('outputs'):
            new_socket = node_socket.OutputSocket(self,
                                                  index=socket_data['index'],
                                                  position=socket_data['position'],
                                                  data_type=socket_data['data_type'],
                                                  label=socket_data['label'],
                                                  max_connections=socket_data['max_connections'])
            new_socket.deserialize(socket_data, hashmap, restore_id=restore_id)
            self.outputs.append(new_socket)

    # Creation methods
    def add_input(self, data_type, label=None, value=None, *args, **kwargs):
        socket = node_socket.InputSocket(self,
                                         index=self.get_new_input_index(),
                                         position=node_socket.Socket.Position.LEFT_TOP,
                                         data_type=data_type,
                                         label=label,
                                         max_connections=1,
                                         value=value,
                                         *args,
                                         **kwargs)
        self.inputs.append(socket)
        return socket

    def add_output(self, data_type, label=None, max_connections=0, value=None, *args, **kwargs):
        socket = node_socket.OutputSocket(self,
                                          index=self.get_new_output_index(),
                                          position=node_socket.Socket.Position.RIGHT_TOP,
                                          data_type=data_type,
                                          label=label,
                                          max_connections=max_connections,
                                          value=value,
                                          *args,
                                          **kwargs)
        self.outputs.append(socket)
        return socket
