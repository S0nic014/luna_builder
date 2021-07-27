import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class BranchNode(luna_node.LunaNode):
    ID = 1
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    DEFAULT_TITLE = 'Branch'
    CATEGORY = 'Utils'
    HEIGHT = 100

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
        self.in_condition = self.add_input(editor_conf.DataType.BOOLEAN)

        self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC, label='True')
        self.out_true = self.exec_out_socket
        self.out_false = self.add_output(editor_conf.DataType.EXEC, label='False')


def register_plugin():
    editor_conf.register_node(BranchNode.ID, BranchNode)
