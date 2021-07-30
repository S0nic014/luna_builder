from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class LoggerNode(luna_node.LunaNode):
    ID = 11
    IS_EXEC = True
    ICON = 'func.png'
    AUTO_INIT_EXECS = True
    DEFAULT_TITLE = 'Log'
    CATEGORY = 'Functions'
    HEIGHT = 180

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(LoggerNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.add_input(editor_conf.DataType.STRING, 'Message')
        self.add_input(editor_conf.DataType.BOOLEAN, 'As Info')
        self.add_input(editor_conf.DataType.BOOLEAN, 'As Warning')
        self.add_input(editor_conf.DataType.BOOLEAN, 'As Error')


def register_plugin():
    editor_conf.register_node(LoggerNode.ID, LoggerNode)
