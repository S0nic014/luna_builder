import imp
from PySide2 import QtCore
from collections import OrderedDict

from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.node_serializable as node_serializable
import luna_builder.editor.node_attrib_widget as node_attrib_widget
imp.reload(graphics_node)


class NodeSignals(QtCore.QObject):
    dirty_changed = QtCore.Signal(bool)
    invalid_changed = QtCore.Signal(bool)


class Node(node_serializable.Serializable):

    TITLE_HEIGHT = 24
    DEFAULT_TITLE = 'Custom Node'
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    ATTRIB_WIDGET = node_attrib_widget.AttribWidget
    INPUT_POSITION = node_socket.Socket.Position.LEFT_TOP.value
    OUTPUT_POSITION = node_socket.Socket.Position.RIGHT_TOP.value

    def __str__(self):
        cls_name = self.__class__.__name__
        nice_id = '{0}..{1}'.format(hex(id(self))[2:5], hex(id(self))[-3:])
        return "<{0} {1}>".format(cls_name, nice_id)

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(Node, self).__init__()
        self.scene = scene
        self.signals = NodeSignals()
        self._title = title if title else self.__class__.DEFAULT_TITLE
        self.inputs = []
        self.outputs = []

        # Evaluation
        self._is_dirty = False
        self._is_invalid = False

        # Members init
        self.init_settings()
        self.init_inner_classes()

        # Add to the scene
        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)
        # Sockets
        self.init_sockets(inputs=inputs, outputs=outputs)
        self.create_connections()

    def init_settings(self):
        self.socket_spacing = 22

    def init_inner_classes(self):
        # Setup graphics
        self.gr_node = graphics_node.QLGraphicsNode(self)

    def init_sockets(self, inputs=[], outputs=[], reset=True):
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

    def create_connections(self):
        self.signals.dirty_changed.connect(self.on_dirty_change)
        self.signals.invalid_changed.connect(self.on_invalid_change)

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

    # ======= Socket Utils ======= #

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

            y = top_offset + available_height / 2.0 + (index - 0.5) * self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets - 1) / 2

        elif position in (node_socket.Socket.Position.LEFT_TOP, node_socket.Socket.Position.RIGHT_TOP):
            # start from bottom
            y = self.gr_node.title_height + self.gr_node.title_horizontal_padding + self.gr_node.edge_roundness + index * self.socket_spacing
        else:
            y = 0

        return [x, y]

    def max_height_of_sockets(self):
        min_size = 30
        max_inputs = len(self.inputs) * self.socket_spacing
        max_outputs = len(self.outputs) * self.socket_spacing
        return max(max_inputs, max_outputs, min_size)

    def max_width_of_socket_labels(self):
        min_width = 180
        max_outputs = 0
        max_inputs = 0

        input_widths = [socket.get_label_width() for socket in self.inputs] or [0, 0]
        output_widths = [socket.get_label_width() for socket in self.outputs] or [0, 0]

        max_inputs = max(input_widths)
        max_outputs = max(output_widths)

        return max(max_inputs + max_outputs, min_width)

    # ======== Update methods ========= #
    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            socket.update_edges()

    def update_socket_positions(self):
        for socket in self.outputs + self.inputs:
            socket.update_positions()

    def remove(self):
        try:
            for socket in self.inputs + self.outputs:
                socket.remove_all_edges()
            self.scene.gr_scene.removeItem(self.gr_node)
            self.gr_node = None
            self.scene.remove_node(self)
        except Exception:
            Logger.exception('Failed to delete node {0}'.format(self))

    # ========= Evaluation ============= #
    def is_dirty(self):
        return self._is_dirty

    def set_dirty(self, value=True):
        self._is_dirty = value
        self.signals.dirty_changed.emit(self._is_dirty)

    def on_dirty_change(self, state):
        self.mark_children_dirty(state)

    def is_invalid(self):
        return self._is_invalid

    def set_invalid(self, value=True):
        self._is_invalid = value
        self.signals.invalid_changed.emit(self._is_invalid)

    def on_invalid_change(self, state):
        if state:
            Logger.debug('{0} marked invalid'.format(self))

    def mark_children_dirty(self, state, start_node=None):
        if not state:
            return
        if start_node in self.list_children():
            Logger.warning('Cycle')
            return
        for child_node in self.list_children():
            child_node.set_dirty(state)
            child_node.mark_children_dirty(state, start_node=self)
            return

    # ========= Serialization methods ========== #

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

        # Deserialize sockets
        for socket_data in data.get('inputs'):
            found = None  # type: node_socket.Socket
            for socket in self.inputs:
                if socket.index == socket_data['index']:
                    found = socket
                    break
            if not found:
                Logger.warning('Deserialization of socket data has not found socket with index {0}'.format(socket_data['index']))
                Logger.debug('Missing socket data: {0}'.format(socket_data))
                data_type = socket_data['data_type']
                value = socket_data.get('value', editor_conf.DataType.get_type(data_type)['default'])
                found = self.add_input(data_type, socket_data['label'], value=value)
            found.deserialize(socket_data, hashmap, restore_id)

        for socket_data in data.get('outputs'):
            found = None
            for socket in self.outputs:
                if socket.index == socket_data['index']:
                    found = socket
                    break
            if found is None:
                Logger.warning('Deserialization of socket data has not found socket with index {0}'.format(socket_data['index']))
                Logger.debug('Missing socket data: {0}'.format(socket_data))
                # we can create new socket for this
                data_type = socket_data['data_type']
                value = socket_data.get('value', editor_conf.DataType.get_type(data_type)['default'])
                found = self.add_output(data_type, socket_data['label'], value=value)
            found.deserialize(socket_data, hashmap, restore_id)
        self.update_socket_positions()

    # ========= Socket creation methods ========== #
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
        self.update_socket_positions()
        return socket

    def add_output(self, data_type, label=None, max_connections=0, value=None, *args, **kwargs):
        if data_type == editor_conf.DataType.EXEC:
            max_connections = 1
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
        self.update_socket_positions()
        return socket

    # ========= Graph Traversal ================ #
    def list_children(self, recursive=False):
        children = []
        for output in self.outputs:
            for child_socket in output.list_connections():
                children.append(child_socket.node)
        if recursive:
            for child_node in children:
                children += child_node.list_children(recursive=True)

        return children

    def list_exec_children(self):
        exec_children = []
        for exec_out in self.list_exec_outputs():
            exec_children += [socket.node for socket in exec_out.list_connections()]
        return exec_children

    def execute(self):
        return 0

    def exec_children(self):
        for node in self.list_exec_children():
            node.execute()

    # ========= Socket finding/data retriving ========= #

    def find_first_input_with_label(self, text):
        result = None
        for socket in self.inputs:
            if socket.label == text:
                result = socket
                break
        return result

    def find_first_input_of_datatype(self, datatype):
        result = None
        for socket in self.inputs:
            if issubclass(socket.data_class, datatype.get('class', type(None))):
                result = socket
                break
        return result

    def get_value(self, socket_name):
        socket = getattr(self, socket_name)
        if not isinstance(socket, node_socket.Socket):
            Logger.error('Socket {0} does not exist.'.format(socket_name))
            raise AttributeError
        return socket.value

    def list_exec_outputs(self):
        return [socket for socket in self.outputs if socket.data_type == editor_conf.DataType.EXEC]

    def list_non_exec_inputs(self):
        return [socket for socket in self.inputs if socket.data_type != editor_conf.DataType.EXEC]

    def list_non_exec_outputs(self):
        return [socket for socket in self.outputs if socket.data_type != editor_conf.DataType.EXEC]
