import imp
from collections import OrderedDict

from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_node)


class Node(node_serializable.Serializable):

    WIDTH = 180
    HEIGHT = 240
    TITLE_HEIGHT = 24
    DEFAULT_TITLE = 'Custom Node'
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    INPUT_POSITION = node_socket.Socket.Position.LEFT_TOP.value
    OUTPUT_POSITION = node_socket.Socket.Position.RIGHT_TOP.value

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(Node, self).__init__()
        self.scene = scene
        self._title = title if title else self.__class__.DEFAULT_TITLE
        self.inputs = []
        self.outputs = []

        self.init_settings()
        self.init_inner_objects()

        # Add to the scene
        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)
        # Sockets
        self.init_sockets(inputs=inputs, outputs=outputs)

    def init_settings(self):
        self.socket_spacing = 22

    def init_inner_objects(self):
        # Setup graphics
        self.gr_node = graphics_node.QLGraphicsNode(self)

    def init_sockets(self, inputs=[], outputs=[], reset=False):
        if reset:
            self.remove_existing_sockets()

        # Create new sockets
        if self.__class__.IS_EXEC and self.__class__.AUTO_INIT_EXECS:
            self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
            self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC, max_connections=1)
        else:
            self.exec_in_socket = self.exec_out_socket = None

        for datatype in inputs:
            self.add_input(datatype, label=None, value=None)

        for datatype in outputs:
            self.add_output(datatype, label=None, value=None)

    def remove_existing_sockets(self):
        if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
            for socket in self.inputs + self.outputs:
                self.scene.gr_scene.removeItem(socket.gr_socket)
            self.inputs = []
            self.outputs = []

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

    def get_socket_position(self, index, position, count_on_this_side=1):
        if position in (node_socket.Socket.Position.LEFT_TOP, node_socket.Socket.Position.LEFT_CENTER, node_socket.Socket.Position.LEFT_BOTTOM):
            x = 0
        else:
            x = self.gr_node.width

        if position in (node_socket.Socket.Position.LEFT_BOTTOM, node_socket.Socket.Position.RIGHT_BOTTOM):
            # start from top
            y = self.gr_node.height - self.gr_node.edge_roundness - self.gr_node.title_horizontal_padding - index * self.socket_spacing
        elif position in (node_socket.Socket.Position.LEFT_CENTER, node_socket.Socket.Position.RIGHT_CENTER):
            num_sockets = count_on_this_side
            node_height = self.gr_node.height
            top_offset = self.gr_node.title_height + 2 * self.gr_node.title_vertical_padding + self.gr_node.edge_padding
            available_height = node_height - top_offset

            total_height_of_all_sockets = num_sockets * self.socket_spacing

            y = top_offset + available_height / 2.0 + (index - 0.5) * self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets - 1) / 2

        elif position in (node_socket.Socket.Position.LEFT_TOP, node_socket.Socket.Position.RIGHT_TOP):
            # start from bottom
            y = self.gr_node.title_height + self.gr_node.title_horizontal_padding + self.gr_node.edge_roundness + index * self.socket_spacing
        else:
            y = 0

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
        self.remove_existing_sockets()
        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        num_inputs = len(data['inputs'])
        num_outputs = len(data['outputs'])

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
                                                 value=socket_data.get('value', editor_conf.DataType.get_type(data_type)['default']),
                                                 count_on_this_side=num_inputs)
            new_socket.deserialize(socket_data, hashmap, restore_id=restore_id)
            self.inputs.append(new_socket)

        for socket_data in data.get('outputs'):
            data_type = socket_data['data_type']
            new_socket = node_socket.OutputSocket(self,
                                                  index=socket_data['index'],
                                                  position=socket_data['position'],
                                                  data_type=data_type,
                                                  label=socket_data['label'],
                                                  max_connections=socket_data['max_connections'],
                                                  value=socket_data.get('value', editor_conf.DataType.get_type(data_type)['default']),
                                                  count_on_this_side=num_outputs)
            new_socket.deserialize(socket_data, hashmap, restore_id=restore_id)
            self.outputs.append(new_socket)

    # Creation methods
    def add_input(self, data_type, label=None, value=None, *args, **kwargs):
        socket = node_socket.InputSocket(self,
                                         index=self.get_new_input_index(),
                                         position=self.__class__.INPUT_POSITION,
                                         data_type=data_type,
                                         label=label,
                                         max_connections=1,
                                         value=value,
                                         count_on_this_side=self.get_new_input_index(),
                                         *args,
                                         **kwargs)
        self.inputs.append(socket)
        return socket

    def add_output(self, data_type, label=None, max_connections=0, value=None, *args, **kwargs):
        socket = node_socket.OutputSocket(self,
                                          index=self.get_new_output_index(),
                                          position=self.__class__.OUTPUT_POSITION,
                                          data_type=data_type,
                                          label=label,
                                          max_connections=max_connections,
                                          value=value,
                                          count_on_this_side=self.get_new_output_index(),
                                          *args,
                                          **kwargs)
        self.outputs.append(socket)
        return socket

    def get_value(self, socket_name):
        socket = getattr(self, socket_name)
        if not isinstance(socket, node_socket.Socket):
            Logger.error('Socket {0} does not exist.'.format(socket_name))
            raise AttributeError
        return socket.value
