from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class WireComponentNode(base_component.AnimComponentNode):
    ID = 20
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Wire'
    CATEGORY = 'Components'
    COMPONENT_CLASS = luna_rig.components.WireComponent

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(WireComponentNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        # Override inputs
        self.in_name.value = self.out_name.value = 'wire'

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.WIRE_COMPONENT

        # Create new inputs
        self.in_curve = self.add_input(editor_conf.DataType.STRING, label='Curve')
        self.in_geometry = self.add_input(editor_conf.DataType.STRING, label='Geometry')
        self.in_dropoff_distance = self.add_input(editor_conf.DataType.NUMERIC, label='Dropoff', value=100.0)
        self.in_num_controls = self.add_input(editor_conf.DataType.NUMERIC, label='Number Controls', value=4)
        self.in_control_lines = self.add_input(editor_conf.DataType.BOOLEAN, label='Control Lines', value=True)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(character=self.in_character.value,
                                                              meta_parent=self.in_meta_parent.value,
                                                              side=self.in_side.value,
                                                              name=self.in_side.value,
                                                              hook=self.in_hook.value,
                                                              tag=self.in_tag.value,
                                                              curve=self.in_curve.value,
                                                              geometry=self.in_geometry.value,
                                                              dropoff_distance=self.in_dropoff_distance.value,
                                                              num_controls=self.in_num_controls.value,
                                                              control_lines=self.in_control_lines.value)
        self.out_self.value = self.component_instance


def register_plugin():
    editor_conf.DataType.register_datatype('WIRE_COMPONENT', luna_rig.components.WireComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Wire Component',
                                           default_value=None)
    editor_conf.register_node(WireComponentNode.ID, WireComponentNode)
