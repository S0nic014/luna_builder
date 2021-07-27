import os
import imp

from PySide2 import QtGui

from luna import Logger
import luna_rig
import luna.static.directories as directories


PALETTE_MIMETYPE = 'luna/x-item'


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
    BOOLEAN = {'index': 3,
               'color': QtGui.QColor("#C40000"),
               'label': 'Condition',
               'class': bool,
               'default': False}
    LIST = {'index': 4,
            'color': QtGui.QColor("#FF52e220"),
            'label': 'List',
            'class': list,
            'default': []}
    CONTROL = {'index': 5,
               'color': QtGui.QColor("#FF0056a6"),
               'label': 'Control',
               'class': luna_rig.Control,
               'default': None}
    COMPONENT = {'index': 6,
                 'color': QtGui.QColor("#FF0056a6"),
                 'label': 'Component',
                 'class': luna_rig.Component,
                 'default': None}
    ANIM_COMPONENT = {'index': 7,
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
        Logger.info('Registered datatype: {0}'.format(type_name))

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


# Exceptions
class ConfException(Exception):
    pass


class InvalidNodeRegistration(ConfException):
    pass


# Plugins
NODE_REGISTER = {}


def register_node(node_id, node_class):
    if node_id in NODE_REGISTER:
        Logger.error('Node with id {0} is already registered as {1}'.format(node_id, node_class))
        raise InvalidNodeRegistration
    NODE_REGISTER[node_id] = node_class
    Logger.debug('Registered node {0}::{1}'.format(node_id, node_class))


def load_plugins():
    Logger.info('Loading rig editor plugins...')
    success_count = 0
    plugin_files = []
    for file_name in os.listdir(directories.EDITOR_PLUGINS_PATH):
        if file_name.endswith('.py') and file_name.startswith('node_'):
            plugin_files.append(os.path.join(directories.EDITOR_PLUGINS_PATH, file_name))

    for path in plugin_files:
        p_name = os.path.basename(path).split('.')[0]
        # TODO: Add condition for Python 3 import
        plugin = imp.load_source('luna_builder.rig_nodes.{0}'.format(p_name), path)
        try:
            plugin.register_plugin()
            success_count += 1
        except Exception:
            Logger.exception('Failed to register')
    Logger.info('Successfully loaded {0} plugins'.format(success_count))


if __name__ == '__main__':
    load_plugins()
