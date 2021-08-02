import luna_rig
from collections import OrderedDict
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ControlNode(luna_node.LunaNode):
    ID = 15
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Control'
    CATEGORY = 'Utils'
    UNIQUE = False

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        super(ControlNode, self).init_sockets(inputs=inputs, outputs=outputs, reset=reset)
        self.in_control = self.add_input(editor_conf.DataType.CONTROL, label='Control')

        self.out_control = self.add_output(editor_conf.DataType.CONTROL, label='Control')
        self.out_character = self.add_output(editor_conf.DataType.CHARACTER, label='Character')
        self.out_transform = self.add_output(editor_conf.DataType.STRING, label='Transform')

    def execute(self):
        control_instance = self.in_control.value  # type:luna_rig.Control
        self.out_character.value = control_instance.character
        self.out_transform.value = control_instance.transform

        # Set new title
        self.title = control_instance.transform.name() if control_instance else self.DEFAULT_TITLE


def register_plugin():
    editor_conf.register_node(ControlNode.ID, ControlNode)
    editor_conf.register_function(luna_rig.Control.connect_via_remap,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Source Plug', editor_conf.DataType.STRING),
                                      ('Destination Plug', editor_conf.DataType.STRING),
                                      ('Destination Plug', editor_conf.DataType.STRING),
                                      ('Remap Name', editor_conf.DataType.STRING),
                                      ('Input Min', editor_conf.DataType.NUMERIC),
                                      ('Input Max', editor_conf.DataType.NUMERIC),
                                      ('Output Min', editor_conf.DataType.NUMERIC),
                                      ('Output Max', editor_conf.DataType.NUMERIC)
                                  ]),
                                  default_values=[None, '', '', 'remap', 0.0, 10.0, 0.0, 1.0],
                                  nice_name='Connect Via Remap',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.add_space,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Space Control', editor_conf.DataType.CONTROL),
                                      ('Space Name', editor_conf.DataType.STRING),
                                      ('Use Offset Matrix', editor_conf.DataType.BOOLEAN)
                                  ]),
                                  default_values=[None, None, 'newSpace', False],
                                  nice_name='Add Space',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.add_world_space,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Use Offset Matrix', editor_conf.DataType.BOOLEAN)
                                  ]),
                                  default_values=[None, False],
                                  nice_name='Add World Space',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.add_orient_switch,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Orient Target', editor_conf.DataType.STRING),
                                      ('Local Parent', editor_conf.DataType.CONTROL),
                                      ('Default State', editor_conf.DataType.BOOLEAN),
                                  ]),
                                  default_values=[None, '', None, True],
                                  nice_name='Add Orient Switch',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.constrain_geometry,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Geometry', editor_conf.DataType.STRING),
                                      ('Scale', editor_conf.DataType.BOOLEAN),
                                      ('Inherits Transfom', editor_conf.DataType.BOOLEAN),
                                  ]),
                                  default_values=[None, '', True, True],
                                  nice_name='Constrain Geometry',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.get_parent,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Generations', editor_conf.DataType.NUMERIC)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Parent', editor_conf.DataType.CONTROL),
                                  ]),
                                  default_values=[None, 1],
                                  nice_name='Get Parent',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.set_parent,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Parent Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Set Parent',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_tag,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Tag', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Tag',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_joint,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Joint', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Joint',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_connected_component,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Anim Component', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  nice_name='Get Component',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_character,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Character', editor_conf.DataType.CHARACTER),
                                  ]),
                                  nice_name='Get Character',
                                  category='Control')
