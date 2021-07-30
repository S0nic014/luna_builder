import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class CharacterNode(base_component.ComponentNode):
    ID = 7
    IS_EXEC = True
    ICON = 'bindpose.png'
    DEFAULT_TITLE = 'Character'
    CATEGORY = 'Components'
    UNIQUE = True
    COMPONENT_CLASS = luna_rig.components.Character

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(CharacterNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.out_self.data_type = editor_conf.DataType.CHARACTER
        self.in_name.value = 'character'
        self.in_tag = self.out_tag = 'character'

        self.out_root_control = self.add_output(editor_conf.DataType.CONTROL, label='Root Control')
        self.out_deform_rig = self.add_output(editor_conf.DataType.PYNODE, label='Deformation Rig')
        self.out_control_rig = self.add_output(editor_conf.DataType.PYNODE, label='Control Rig')
        self.out_geometry_grp = self.add_output(editor_conf.DataType.PYNODE, label='Geometry Group')
        self.out_controls = self.add_output(editor_conf.DataType.LIST, label='Controls')
        self.out_bind_joints = self.add_output(editor_conf.DataType.LIST, label='Bind Joints')


def register_plugin():
    editor_conf.register_node(CharacterNode.ID, CharacterNode)
    base_component.register_plugin()
