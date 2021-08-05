from luna import Logger
import luna_builder.rig_nodes.luna_node as luna_node
import luna_builder.editor.editor_conf as editor_conf


class VarNode(luna_node.LunaNode):
    ID = None
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    DEFAULT_TITLE = ''
    CATEGORY = editor_conf.INTERNAL_CATEGORY

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        self._var_name = None
        super(VarNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    @property
    def var_name(self):
        return self._var_name

    @var_name.setter
    def var_name(self, name):
        self._var_name = name
        self.title = '{0} {1}'.format(self.DEFAULT_TITLE, self._var_name)
        self.init_sockets()

    def serialize(self):
        result = super(VarNode, self).serialize()
        result['var_name'] = self.var_name
        return result

    def pre_deserilization(self, data):
        self.var_name = data.get('var_name')

    def get_attrib_widget(self):
        return None


class SetNode(VarNode):
    ID = editor_conf.SET_NODE_ID
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    ICON = None
    DEFAULT_TITLE = 'Set'

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(SetNode, self).init_sockets(inputs, outputs, reset)
        if not self.var_name:
            return

        self.in_value = self.add_input(self.scene.vars.get_data_type(self.var_name, as_dict=True))

    def execute(self):
        if not self.var_name:
            Logger.error('{0}: var_name is not set'.format(self))
            raise ValueError
        self.scene.vars.set_value(self.var_name, self.in_value.value)


class GetNode(VarNode):
    ID = editor_conf.GET_NODE_ID
    IS_EXEC = False
    AUTO_INIT_EXECS = False
    ICON = None
    DEFAULT_TITLE = 'Get'

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        if not self.var_name:
            return

        super(GetNode, self).init_sockets(inputs, outputs, reset)
        self.out_value = self.add_output(self.scene.vars.get_data_type(self.var_name, as_dict=True), value=self.scene.vars.get_value(self.var_name))


def register_plugin():
    editor_conf.register_node(SetNode.ID, SetNode)
    editor_conf.register_node(GetNode.ID, GetNode)
