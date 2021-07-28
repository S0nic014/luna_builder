import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ComponentNode(luna_node.LunaNode):

    DEFAULT_TITLE = 'Component'
    COMPONENT_CLASS = luna_rig.Component

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(ComponentNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)
        self.component_instance = None

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
        self.out_meta_children = self.add_output(editor_conf.DataType.LIST, label='Children')
        self.out_side = self.add_output(editor_conf.DataType.STRING, label='Side', value='c')
        self.out_name = self.add_output(editor_conf.DataType.STRING, label='Name', value='component')
        self.out_tag = self.add_output(editor_conf.DataType.STRING, label='Tag', value='')


class AnimComponentNode(ComponentNode):

    DEFAULT_TITLE = 'Anim Component'
    HEIGHT = 260
    COMPONENT_CLASS = luna_rig.AnimComponent

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(AnimComponentNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        # Override types
        self.out_self.data_type = editor_conf.DataType.ANIM_COMPONENT
        self.in_meta_parent.data_type = self.out_meta_parent.data_type = editor_conf.DataType.ANIM_COMPONENT

        # Override values
        self.in_name.value = 'anim_component'
        self.in_character = self.add_input(editor_conf.DataType.CHARACTER, label='Character')
        self.in_hook = self.add_input(editor_conf.DataType.NUMERIC, label='In Hook')

        self.out_character = self.add_output(editor_conf.DataType.CHARACTER, label='Character')
        self.out_in_hook = self.add_output(editor_conf.DataType.NUMERIC, label='In Hook')
        self.out_hooks_list = self.add_output(editor_conf.DataType.LIST, label='Hooks List')
        self.out_controls = self.add_output(editor_conf.DataType.LIST, label='Controls')
        self.out_bind_joints = self.add_output(editor_conf.DataType.LIST, label='Bind Joints')
        self.out_ctl_chain = self.add_output(editor_conf.DataType.LIST, label='Ctl Chain')

        self.in_hook.value = self.out_in_hook.value = None


def register_plugin():
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.character,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict={'AnimComponent': editor_conf.DataType.ANIM_COMPONENT},
                                  outputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  nice_name='Get Character')
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.in_hook_index,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict={'AnimComponent': editor_conf.DataType.ANIM_COMPONENT},
                                  outputs_dict={'Hook Index': editor_conf.DataType.NUMERIC},
                                  nice_name='Get In Hook Index')
