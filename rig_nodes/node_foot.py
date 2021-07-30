import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class FootComponentNode(base_component.AnimComponentNode):
    ID = 10
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Foot'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.FootComponent

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(FootComponentNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.in_name = self.out_name = 'foot'
        self.in_tag = self.out_tag = 'body'
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)
        self.in_rv_chain = self.add_input(editor_conf.DataType.STRING, label='Reverse Chain', value=None)
        self.in_foot_loc_grp = self.add_input(editor_conf.DataType.STRING, label='Foot Locators Group', value=None)
        self.in_roll_axis = self.add_input(editor_conf.DataType.STRING, label='Rotate Axis', value='ry')

        self.out_roll_axis = self.add_output(editor_conf.DataType.STRING, label='Foot Locators Group', value=self.in_roll_axis.value)
        self.out_fk_control = self.add_output(editor_conf.DataType.CONTROL, label='FK Control', value=None)


def register_plugin():
    editor_conf.register_node(FootComponentNode.ID, FootComponentNode)
