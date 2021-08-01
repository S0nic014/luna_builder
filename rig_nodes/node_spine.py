from luna import Logger
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class SpineNode(base_component.AnimComponentNode):
    ID = None
    IS_EXEC = True
    ICON = 'body.png'
    DEFAULT_TITLE = 'Spine'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = None

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(SpineNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.in_name.value = self.out_name.value = 'spine'
        self.in_tag.value = self.out_tag.value = 'body'
        self.out_root_control = self.add_output(editor_conf.DataType.CONTROL, label='Root Control')
        self.out_hips_control = self.add_output(editor_conf.DataType.CONTROL, label='Hips Control')
        self.out_chest_control = self.add_output(editor_conf.DataType.CONTROL, label='Chest Control')
        self.out_ik_curve = self.add_output(editor_conf.DataType.PYNODE, label='IK Curve')


class FKIKSpineNode(SpineNode):
    ID = 8
    DEFAULT_TITLE = 'FKIK Spine'
    COMPONENT_CLASS = luna_rig.components.FKIKSpineComponent

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(FKIKSpineNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)

        self.out_hook_root = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Root', value=self.COMPONENT_CLASS.Hooks.ROOT.value)
        self.out_hook_hips = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Hips', value=self.COMPONENT_CLASS.Hooks.HIPS.value)
        self.out_hook_mid = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Mid', value=self.COMPONENT_CLASS.Hooks.MID.value)
        self.out_hook_chest = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Chest', value=self.COMPONENT_CLASS.Hooks.CHEST.value)
        self.out_mid_control = self.add_output(editor_conf.DataType.CONTROL, label='Mid Control')
        self.out_fk1_control = self.add_output(editor_conf.DataType.CONTROL, label='FK1 Control')
        self.out_fk2_control = self.add_output(editor_conf.DataType.CONTROL, label='FK2 Control')
        self.out_pivot_control = self.add_output(editor_conf.DataType.CONTROL, label='Pivot Control')

    def execute(self):
        try:
            self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value,
                                                                  hook=self.in_hook.value,
                                                                  character=self.in_character.value,
                                                                  side=self.in_side.value,
                                                                  name=self.in_name.value,
                                                                  start_joint=self.in_start_joint.value,
                                                                  end_joint=self.in_end_joint.value,
                                                                  tag=self.in_tag.value)
            # Set outputs
            self.out_self.value = self.component_instance
            self.out_bind_joints.value = self.component_instance.bind_joints
            self.out_controls.value = self.component_instance.controls
            self.out_chest_control.value = self.component_instance.chest_control
            self.out_ctl_chain.value = self.component_instance.ctl_chain
            self.out_fk1_control.value = self.component_instance.fk1_control
            self.out_fk2_control.value = self.component_instance.fk2_control
            self.out_hips_control.value = self.component_instance.hips_control
            self.out_mid_control.value = self.component_instance.mid_control
            self.out_root_control.value = self.component_instance.root_control
        except Exception:
            Logger.exception('Failed to create FKIK Spine')
            return 1
        return 0


def register_plugin():
    editor_conf.register_node(FKIKSpineNode.ID, FKIKSpineNode)
