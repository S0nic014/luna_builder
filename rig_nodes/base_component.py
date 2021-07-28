import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ComponentNode(luna_node.LunaNode):

    DEFAULT_TITLE = 'Component'

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(ComponentNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        # Inputs
        self.in_meta_parent = self.add_input(editor_conf.DataType.COMPONENT, label='Parent', value=None)
        self.in_side = self.add_input(editor_conf.DataType.STRING, label='Side', value='c')
        self.in_name = self.add_input(editor_conf.DataType.STRING, label='Name', value='component')
        self.in_tag = self.add_input(editor_conf.DataType.STRING, label='Tag', value='')

        # Outputs
        # Inputs
        self.out_self = self.add_output(editor_conf.DataType.COMPONENT, label='Self', value=None)
        self.out_meta_parent = self.add_output(editor_conf.DataType.COMPONENT, label='Parent', value=None)
        self.out_meta_childrent = self.add_output(editor_conf.DataType.LIST, label='Children')
        self.out_side = self.add_output(editor_conf.DataType.STRING, label='Side', value='c')
        self.out_name = self.add_output(editor_conf.DataType.STRING, label='Name', value='component')
        self.out_tag = self.add_output(editor_conf.DataType.STRING, label='Tag', value='')


class AnimComponentNode(ComponentNode):

    DEFAULT_TITLE = 'Anim Component'
    HEIGHT = 260

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(AnimComponentNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.in_name.value = 'anim_component'

        # FIXME: Change DataType.COMPONENT to DataType.CHARACTER
        self.in_character = self.add_input(editor_conf.DataType.COMPONENT, label='Character')
        self.in_hook = self.add_input(editor_conf.DataType.NUMERIC, label='Hook')
        self.in_hook.value = None

        # FIXME: Change DataType.COMPONENT to DataType.CHARACTER
        self.out_character = self.add_output(editor_conf.DataType.COMPONENT, label='Character')
        self.out_hooks_list = self.add_output(editor_conf.DataType.LIST, label='Hooks List')
        self.out_controls = self.add_output(editor_conf.DataType.LIST, label='Controls')
        self.out_bind_joints = self.add_output(editor_conf.DataType.LIST, label='Bind Joints')
        self.out_ctl_chain = self.add_output(editor_conf.DataType.LIST, label='Ctl Chain')

    def init_out_hooks_sockets(self):
        pass
