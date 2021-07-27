import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class GraphInputNode(luna_node.LunaNode):
    ID = 3
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    DEFAULT_TITLE = 'Input'
    HEIGHT = 80
    CATEGORY = 'Utils'
    UNIQUE = True
    OUTPUT_POSITION = 5

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        self.exec_in_socket = None
        self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC)


class GraphOutputNode(luna_node.LunaNode):
    ID = 4
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    DEFAULT_TITLE = 'Output'
    HEIGHT = 80
    CATEGORY = 'Utils'
    UNIQUE = True
    INPUT_POSITION = 2

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
        self.exec_out_socket = None


def register_plugin():
    editor_conf.register_node(GraphInputNode.ID, GraphInputNode)
    editor_conf.register_node(GraphOutputNode.ID, GraphOutputNode)
