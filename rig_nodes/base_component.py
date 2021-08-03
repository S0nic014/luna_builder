from collections import OrderedDict
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
        self.update_node_title()

    def create_connections(self):
        super(ComponentNode, self).create_connections()
        self.in_name.signals.value_changed.connect(self.update_node_title)
        self.in_side.signals.value_changed.connect(self.update_node_title)

    def update_node_title(self):
        self.title = "{0} - {1} ({2})".format(self.DEFAULT_TITLE, self.in_name.value, self.in_side.value)


class AnimComponentNode(ComponentNode):

    DEFAULT_TITLE = 'Anim Component'
    COMPONENT_CLASS = luna_rig.AnimComponent

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(AnimComponentNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        # Override types
        self.out_self.data_type = editor_conf.DataType.ANIM_COMPONENT
        self.in_meta_parent.data_type = self.out_meta_parent.data_type = editor_conf.DataType.ANIM_COMPONENT
        self.in_name.value = 'anim_component'

        # Inputs
        self.in_character = self.add_input(editor_conf.DataType.CHARACTER, label='Character')
        self.in_hook = self.add_input(editor_conf.DataType.NUMERIC, label='In Hook')

        # Outputs
        self.out_character = self.add_output(editor_conf.DataType.CHARACTER, label='Character')
        self.out_in_hook = self.add_output(editor_conf.DataType.NUMERIC, label='In Hook')

        # Set default
        self.in_hook.value = None


def register_plugin():
    # Component methods
    editor_conf.register_function(ComponentNode.COMPONENT_CLASS.get_meta_parent,
                                  editor_conf.DataType.COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Component', editor_conf.DataType.COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Parent Component', editor_conf.DataType.COMPONENT),
                                  ]),
                                  nice_name='Get Parent',
                                  category='Component')
    editor_conf.register_function(ComponentNode.COMPONENT_CLASS.get_meta_children,
                                  editor_conf.DataType.COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Component', editor_conf.DataType.COMPONENT),
                                      ('By Tag', editor_conf.DataType.STRING)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Children', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='Get Children',
                                  category='Component')

    # Anim Component methods
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_meta_parent,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Parent AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  nice_name='Get Parent',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_character,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict={'AnimComponent': editor_conf.DataType.ANIM_COMPONENT},
                                  outputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  nice_name='Get Character',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_in_hook_index,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict={'AnimComponent': editor_conf.DataType.ANIM_COMPONENT},
                                  outputs_dict={'Hook Index': editor_conf.DataType.NUMERIC},
                                  nice_name='Get In Hook Index',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.list_controls,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Controls', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='List Controls',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_ctl_chain,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Joint Chain', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='Get Ctl Chain',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_character,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Character', editor_conf.DataType.CHARACTER),
                                  ]),
                                  nice_name='Get Character',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_bind_joints,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Bind Joints', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='Get Bind Joints',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_root,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Root Group', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Root',
                                  category='Anim Component')
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_hook_transform,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                      ('Hook Index', editor_conf.DataType.NUMERIC)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Transform', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Hook Transform',
                                  category='Anim Component')
