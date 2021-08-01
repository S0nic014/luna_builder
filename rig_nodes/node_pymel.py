import pymel.core as pm
from collections import OrderedDict
import luna_builder.editor.editor_conf as editor_conf


def register_plugin():
    editor_conf.register_function(pm.parent,
                                  None,
                                  OrderedDict([
                                      ('Child', editor_conf.DataType.STRING),
                                      ('Parent', editor_conf.DataType.STRING)]),
                                  nice_name='Parent')
