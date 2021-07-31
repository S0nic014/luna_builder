import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ConstantNode(luna_node.LunaNode):
    IS_EXEC = False
    DEFAULT_TITLE = 'Constant'
    CATEGORY = 'Utils'
    CONSTANT_DATA_TYPE = None

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        self.data_type = getattr(editor_conf.DataType, self.CONSTANT_DATA_TYPE)
        super(ConstantNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        self.in_value = self.add_input(self.data_type, label='Value', value=None)
        self.in_value.gr_socket.hide()
        self.out_value = self.add_output(self.data_type, label='Value', value=None)


class ConstantFloatNode(ConstantNode):
    ID = 2
    CONSTANT_DATA_TYPE = 'NUMERIC'
    DEFAULT_TITLE = 'Number'


class ConstantStringNode(ConstantNode):
    ID = 12
    CONSTANT_DATA_TYPE = 'STRING'
    DEFAULT_TITLE = 'String'


class ConstantPyNodeNode(ConstantNode):
    ID = 13
    CONSTANT_DATA_TYPE = 'PYNODE'
    DEFAULT_TITLE = 'PyNode'


class ConstantBoolNode(ConstantNode):
    ID = 14
    CONSTANT_DATA_TYPE = 'BOOLEAN'
    DEFAULT_TITLE = 'Boolean'


def register_plugin():
    for cls in [ConstantFloatNode, ConstantStringNode, ConstantPyNodeNode, ConstantBoolNode]:
        editor_conf.register_node(cls.ID, cls)
