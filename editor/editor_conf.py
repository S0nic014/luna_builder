import os
import imp

from PySide2 import QtGui

import pymel.core as pm
from luna import Logger
import luna_rig
import luna.static.directories as directories


# ====== CONSTANTS ======== #
PALETTE_MIMETYPE = 'luna/x-item'
FUNC_NODE_ID = 100
INPUT_NODE_ID = 101
OUTPUT_NODE_ID = 102
UNBOUND_FUNCTION_DATATYPE = -1

# ====== EXCEPTIONS ======== #


class ConfException(Exception):
    pass


class InvalidNodeRegistration(ConfException):
    pass


class NodeIDNotFound(ConfException):
    pass


class DataType(object):

    EXEC = {'index': 0,
            'color': QtGui.QColor("#FFFFFF"),
            'label': '',
            'class': type(None),
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
    CHARACTER = {'index': 8,
                 'color': QtGui.QColor("#FF0056a6"),
                 'label': 'Character',
                 'class': luna_rig.components.Character,
                 'default': None}

    @classmethod
    def runtime_types(cls):
        return [cls.COMPONENT, cls.LIST, cls.CONTROL]

    @classmethod
    def list_types(cls):
        return [(dt, desc) for dt, desc in cls.__dict__.items() if isinstance(desc, dict)]

    @classmethod
    def list_basetypes(cls, of_type):
        basetypes = [typ for typ in cls.list_types() if issubclass(of_type, typ[1]['class'])]
        return basetypes

    @ classmethod
    def register_datatype(cls, type_name, color, label='custom_data', type_class=None, default_value=None):
        type_dict = {'index': cls._get_new_index(),
                     'color': color if isinstance(color, QtGui.QColor) else QtGui.QColor(color),
                     'label': label.capitalize(),
                     'class': type_class,
                     'default': default_value}
        setattr(cls, type_name, type_dict)
        Logger.info('Registered datatype: {0}'.format(type_name))

    @ classmethod
    def get_type(cls, index, name_only=False):
        if index == UNBOUND_FUNCTION_DATATYPE:
            return None

        try:
            type_name = [dt for dt, desc in cls.__dict__.items() if isinstance(desc, dict) and desc.get('index') == index][0]
        except IndexError:
            Logger.exception('Failed to find datatype with index {0}'.format(index))
            raise IndexError
        else:
            if name_only:
                return type_name
            return cls.__dict__[type_name]

    @ classmethod
    def _get_new_index(cls):
        return len([mp for mp in cls.__dict__.values() if isinstance(mp, dict)])


# ========== REGISTERS =========== #
NODE_REGISTER = {}

FUNCTION_REGISTER = {}


def register_node(node_id, node_class):
    if node_id in NODE_REGISTER:
        Logger.error('Node with id {0} is already registered as {1}'.format(node_id, node_class))
        raise InvalidNodeRegistration
    NODE_REGISTER[node_id] = node_class
    Logger.debug('Registered node {0}::{1}'.format(node_id, node_class))


def get_node_class_from_id(node_id):
    if node_id not in NODE_REGISTER:
        Logger.error('Node ID {0} was not found in register'.format(node_id))
        raise NodeIDNotFound
    return NODE_REGISTER[node_id]


# ========== FUNCTIONS =========== #
def register_function(func,
                      source_datatype,
                      inputs_dict={},
                      outputs_dict={},
                      default_values=[],
                      nice_name=None,
                      docstring='',
                      icon='func.png'):
    # Get datatype index if source_datatype is not int
    if not isinstance(source_datatype, int):
        if not source_datatype:
            dt_index = UNBOUND_FUNCTION_DATATYPE
        else:
            dt_index = source_datatype.get('index')
        dt_name = DataType.get_type(dt_index, name_only=True) if dt_index else None

    # Create register signature
    if source_datatype:
        src_class = source_datatype.get('class')
        if src_class:
            signature = "{0}.{1}.{2}".format(src_class.__module__, src_class.__name__, func.__name__)
        else:
            signature = "{0}.{1}".format(func.__module__, func.__name__)
    else:
        signature = "{0}.{1}".format(func.__module__, func.__name__)

    # Create function description
    func_dict = {'ref': func,
                 'inputs': inputs_dict,
                 'outputs': outputs_dict,
                 'doc': docstring,
                 'icon': icon,
                 'nice_name': nice_name,
                 'default_values': default_values}

    # Store function in the register
    if dt_index not in FUNCTION_REGISTER:
        FUNCTION_REGISTER[dt_index] = {}
    FUNCTION_REGISTER[dt_index][signature] = func_dict
    Logger.debug('Registered function for datatype {0} ({1}):'.format(dt_name, dt_index))
    Logger.debug('>    {0}: {1}\n'.format(signature, func_dict))


def get_functions_map_from_datatype(datatype):
    func_map = FUNCTION_REGISTER.get(datatype['index'])  # type: dict
    return func_map


def get_function_from_signature(signature):
    for dt_func_map in FUNCTION_REGISTER.values():
        if signature in dt_func_map:
            return dt_func_map[signature]
    return None


def get_class_name_from_signature(signature):
    return signature.split('.')[-2]


# ========== PLUGINS =========== #
def load_plugins():
    Logger.info('Loading rig editor plugins...')
    success_count = 0
    plugin_files = []
    plugin_paths = []

    for file_name in os.listdir(directories.EDITOR_PLUGINS_PATH):
        if file_name.endswith('.py') and file_name.startswith('node_'):
            plugin_files.append(file_name)
    # Move core files to the front
    plugin_files.insert(0, plugin_files.pop(plugin_files.index('node_function.py')))
    plugin_files.insert(1, plugin_files.pop(plugin_files.index('node_character.py')))
    plugin_paths = [os.path.join(directories.EDITOR_PLUGINS_PATH, file_name) for file_name in plugin_files]

    # Dynamically import plugin files
    for path in plugin_paths:
        p_name = os.path.basename(path).split('.')[0]
        # TODO: Add condition for Python 3 import
        plugin = imp.load_source('luna_builder.rig_nodes.{0}'.format(p_name), path)
        try:
            plugin.register_plugin()
            success_count += 1
        except Exception:
            Logger.exception('Failed to register')
    Logger.info('Successfully loaded {0} plugins'.format(success_count))


def reload_plugins():
    NODE_REGISTER.clear()
    FUNCTION_REGISTER.clear()
    load_plugins()
