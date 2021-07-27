from PySide2 import QtCore
from PySide2 import QtGui
from luna import Logger
import luna_rig


PALETTE_MIMETYPE = 'luna/x-item'


''' TODO: NODE Classes: LunaNode -> ComponentNode -> AnimComponentNode-> Per Component
                                                  -> CharacterComponent
                                 -> Function Node
                                 -> Control Node
'''


NODE_REGISTER = {
    'Character Component': 1,
    'Simple Component': 2
}


class DataType(object):

    EXEC = {'index': 0,
            'color': QtGui.QColor("#FFFFFF"),
            'label': '',
            'class': None,
            'default': None}
    STRING = {'index': 1,
              'color': QtGui.QColor("#FF52e220"),
              'label': 'Name',
              'class': str,
              'default': ''}
    NUMERIC = {'index': 2,
               'color': QtGui.QColor("#FFFF7700"),
               'label': 'Number',
               'class': float,
               'default': 0.0}
    CONTROL = {'index': 3,
               'color': QtGui.QColor("#FF0056a6"),
               'label': 'Control',
               'class': luna_rig.Control,
               'default': None}
    COMPONENT = {'index': 4,
                 'color': QtGui.QColor("#FF0056a6"),
                 'label': 'Component',
                 'class': luna_rig.Component,
                 'default': None}
    ANIM_COMPONENT = {'index': 5,
                      'color': QtGui.QColor("#FF0056a6"),
                      'label': 'AnimComponent',
                      'class': luna_rig.AnimComponent,
                      'default': None}

    @classmethod
    def register_datatype(cls, type_name, color, label='custom_data', type_class=None, default_value=None):
        type_dict = {'index': cls._get_new_index(),
                     'color': color if isinstance(color, QtGui.QColor) else QtGui.QColor(color),
                     'label': label.capitalize(),
                     'class': type_class,
                     'default': default_value}
        setattr(cls, type_name, type_dict)

    @classmethod
    def get_type(cls, index, name_only=False):
        try:
            type_name = [dt for dt, desc in cls.__dict__.items() if isinstance(desc, dict) and desc.get('index') == index][0]
        except IndexError:
            Logger.exception('Failed to find datatype with index {0}'.format(index))
            raise IndexError
        else:
            if name_only:
                return type_name
            return cls.__dict__[type_name]

    @classmethod
    def _get_new_index(cls):
        return len([mp for mp in cls.__dict__.values() if isinstance(mp, dict)])
