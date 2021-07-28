import luna_builder.editor.node_node as node_node


class LunaNode(node_node.Node):

    ID = None
    ICON = None
    DEFAULT_TITLE = 'Luna Node'
    UNIQUE = False
    CATEGORY = 'Utils'

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(LunaNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    def serialize(self):
        data_dict = super(LunaNode, self).serialize()
        data_dict['node_id'] = self.__class__.ID
        return data_dict

    def execute(self):
        pass
