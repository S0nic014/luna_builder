from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class FunctionNode(luna_node.LunaNode):
    ID = editor_conf.FUNC_NODE_ID
    IS_EXEC = True
    ICON = 'func.png'
    AUTO_INIT_EXECS = True
    DEFAULT_TITLE = 'Function'
    CATEGORY = 'Functions'
    HEIGHT = 180

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        self._func_signature = ''
        self._func_desc = {}
        super(FunctionNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(FunctionNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        if not self._func_desc:
            return

        for socket_name, socket_datatype in self.func_desc.get('inputs').items():
            self.add_input(socket_datatype, socket_name)

        for socket_name, socket_datatype in self.func_desc.get('outputs').items():
            self.add_output(socket_datatype, socket_name)

    @property
    def func_signature(self):
        return self._func_signature

    @func_signature.setter
    def func_signature(self, value):
        self.set_signature_without_reinit(value)
        self.init_sockets(reset=True)

    def set_signature_without_reinit(self, signature):
        self._func_signature = signature
        self._func_desc = editor_conf.get_function_from_signature(signature)
        if not self._func_signature:
            Logger.warning('{0}: Missing function signature!'.format(self))

    @property
    def func_desc(self):
        return self._func_desc

    def serialize(self):
        res = super(FunctionNode, self).serialize()
        res['func_signature'] = self.func_signature
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        super(FunctionNode, self).deserialize(data, hashmap=hashmap, restore_id=restore_id)
        self.set_signature_without_reinit(data.get('func_signature'))

    def execute(self):
        pass


def register_plugin():
    editor_conf.register_node(FunctionNode.ID, FunctionNode)
