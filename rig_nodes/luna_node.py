import luna_builder.editor.node_node as node_node


class LunaNode(node_node.Node):

    ID = None
    ICON = None
    PALETTE_NAME = node_node.Node.DEFAULT_TITLE
    CATEGORY = 'Utils'

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(LunaNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    def execute(self):
        pass
