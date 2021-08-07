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

    def set_var_name(self, name, init_sockets=False):
        self._var_name = name
        if name not in self.scene.vars._vars.keys():
            Logger.error('Variable "{0}" no longer exists'.format(name))
            self.set_invalid(True)
            return

        self.title = '{0} {1}'.format(self.DEFAULT_TITLE, self._var_name)
        if init_sockets:
            self.init_sockets()

    def update(self):
        raise NotImplementedError

    def verify(self):
        return self.var_name in self.scene.vars._vars.keys()

    def serialize(self):
        result = super(VarNode, self).serialize()
        result['var_name'] = self.var_name
        return result

    def pre_deserilization(self, data):
        self.set_var_name(data.get('var_name'), init_sockets=True)

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

    def update(self):
        var_type = self.scene.vars.get_data_type(self.var_name, as_dict=True)
        if not self.in_value.data_type == var_type:
            self.in_value.label = var_type['label']
            self.in_value.data_type = var_type
            self.in_value.update_positions()

    def execute(self):
        if not self.var_name:
            Logger.error('{0}: var_name is not set'.format(self))
            raise ValueError
        self.scene.vars.set_value(self.var_name, self.in_value.value)


class GetNode(VarNode):
    ID = editor_conf.GET_NODE_ID
    IS_EXEC = False
    STATUS_ICON = False
    AUTO_INIT_EXECS = False
    ICON = None
    DEFAULT_TITLE = 'Get'

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        if not self.var_name:
            return

        super(GetNode, self).init_sockets(inputs, outputs, reset)
        self.out_value = self.add_output(self.scene.vars.get_data_type(self.var_name, as_dict=True), value=self.scene.vars.get_value(self.var_name))

    def update(self):
        var_value = self.scene.vars.get_value(self.var_name)
        var_type = self.scene.vars.get_data_type(self.var_name, as_dict=True)
        self.out_value.value = var_value
        if not self.out_value.data_type == var_type:
            self.out_value.label = var_type['label']
            self.out_value.data_type = var_type
            self.out_value.update_positions()


def register_plugin():
    editor_conf.register_node(SetNode.ID, SetNode)
    editor_conf.register_node(GetNode.ID, GetNode)
