import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class FKIKComponentNode(base_component.AnimComponentNode):
    ID = 9
    IS_EXEC = True
    ICON = 'ikfk.png'
    DEFAULT_TITLE = 'FKIK'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.FKIKComponent

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(FKIKComponentNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)

        self.in_name.value = self.out_name.value = 'fkik_component'
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)
        self.in_ik_world_orient = self.add_input(editor_conf.DataType.BOOLEAN, label='IK World Orient', value=False)
        self.in_default_state = self.add_input(editor_conf.DataType.BOOLEAN, label='Default to IK')
        self.in_param_locator = self.add_input(editor_conf.DataType.STRING, 'Param Control Locator')

        self.out_hook_start_jnt = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Start', value=self.COMPONENT_CLASS.Hooks.START_JNT.value)
        self.out_hook_start_jnt = self.add_output(editor_conf.DataType.NUMERIC, label='Hook End', value=self.COMPONENT_CLASS.Hooks.END_JNT.value)
        self.out_ik_control = self.add_output(editor_conf.DataType.CONTROL, label='IK Control')
        self.out_pv_control = self.add_output(editor_conf.DataType.CONTROL, label='PV Control')
        self.out_param_controls = self.add_output(editor_conf.DataType.LIST, label='Param Control')
        self.out_fk_controls = self.add_output(editor_conf.DataType.LIST, label='FK Controls')
        self.out_ik_handle = self.add_output(editor_conf.DataType.PYNODE, label='IK Handle')

    def execute(self):
        pass


def register_plugin():
    editor_conf.register_node(FKIKComponentNode.ID, FKIKComponentNode)
