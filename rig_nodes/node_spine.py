import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class SpineNode(base_component.AnimComponentNode):
    ID = None
    IS_EXEC = True
    ICON = 'body.png'
    HEIGHT = 320
    WIDTH = 240
    DEFAULT_TITLE = 'Spine'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = None

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(SpineNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.in_name.value = self.out_name.value = 'spine'
        self.in_tag = self.out_tag = 'body'
        self.out_root_control = self.add_output(editor_conf.DataType.CONTROL, label='Root Control')
        self.out_hips_control = self.add_output(editor_conf.DataType.CONTROL, label='Hips Control')
        self.out_chest_control = self.add_output(editor_conf.DataType.CONTROL, label='Chest Control')
        self.out_ik_curve = self.add_output(editor_conf.DataType.PYNODE, label='IK Curve')


class FKIKSpineNode(SpineNode):
    ID = 8
    HEIGHT = 600
    DEFAULT_TITLE = 'Spine (FKIK)'
    COMPONENT_CLASS = luna_rig.components.FKIKSpineComponent

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(FKIKSpineNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)

        self.out_hook_root = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Root', value=self.COMPONENT_CLASS.Hooks.ROOT.value)
        self.out_hook_root = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Hips', value=self.COMPONENT_CLASS.Hooks.HIPS.value)
        self.out_hook_root = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Mid', value=self.COMPONENT_CLASS.Hooks.MID.value)
        self.out_hook_root = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Chest', value=self.COMPONENT_CLASS.Hooks.CHEST.value)
        self.out_mid_control = self.add_output(editor_conf.DataType.CONTROL, label='Mid Control')
        self.out_fk1_control = self.add_output(editor_conf.DataType.CONTROL, label='FK1 Control')
        self.out_fk2_control = self.add_output(editor_conf.DataType.CONTROL, label='FK2 Control')
        self.out_pivot_control = self.add_output(editor_conf.DataType.CONTROL, label='Pivot Control')


def register_plugin():
    editor_conf.register_node(FKIKSpineNode.ID, FKIKSpineNode)
