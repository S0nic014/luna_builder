import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ConstantNode(luna_node.LunaNode):
    ID = 2
    IS_EXEC = False
    HEIGHT = 80
    DEFAULT_TITLE = 'Constant'
    CATEGORY = 'Utils'

    def __init__(self, scene, title=None, inputs=[], outputs=[], data_type=editor_conf.DataType.NUMERIC):
        self.data_type = data_type
        super(ConstantNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        self.out_value = self.add_output(self.data_type, label='Value', value=None)

    def set_data_type(self, typ):
        self.data_type = typ
        self.out_value.data_type = typ

    def serialize(self):
        data_dict = super(ConstantNode, self).serialize()
        data_dict['data_type'] = self.data_type.get('index')
        return data_dict

    def deserialize(self, data, hashmap={}, restore_id=True):
        super(ConstantNode, self).deserialize(data, hashmap=hashmap, restore_id=restore_id)
        self.data_type = editor_conf.DataType.get_type(data.get('data_type'))


def register_plugin():
    editor_conf.register_node(ConstantNode.ID, ConstantNode)
