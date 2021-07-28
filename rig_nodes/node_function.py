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

    def execute(self):
        pass


def register_plugin():
    editor_conf.register_node(FunctionNode.ID, FunctionNode)
