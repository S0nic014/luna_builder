import luna_rig
from luna import Logger
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
        self.in_tag.value = self.out_tag.value = 'character'

        self.out_root_control = self.add_output(editor_conf.DataType.CONTROL, label='Root Control')
        self.out_deform_rig = self.add_output(editor_conf.DataType.PYNODE, label='Deformation Rig')
        self.out_control_rig = self.add_output(editor_conf.DataType.PYNODE, label='Control Rig')
        self.out_geometry_grp = self.add_output(editor_conf.DataType.PYNODE, label='Geometry Group')

    def execute(self):
        try:
            self.component_instance = self.COMPONENT_CLASS.create(self.in_meta_parent.value, name=self.in_name.value, tag=self.in_tag.value)
            # Set outputs
            self.out_self.value = self.component_instance
            self.out_meta_parent.value = self.component_instance.meta_parent
            self.out_root_control.value = self.component_instance.root_control.transform
            self.out_deform_rig.value = self.component_instance.deformation_rig
            self.out_control_rig.value = self.component_instance.control_rig
            self.out_geometry_grp.value = self.component_instance.geometry_grp

        except Exception:
            Logger.exception('Failed to create character component')
            return 1


def register_plugin():
    editor_conf.register_node(CharacterNode.ID, CharacterNode)
    base_component.register_plugin()
