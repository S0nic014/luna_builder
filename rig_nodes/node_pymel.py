import pymel.core as pm
import luna_builder.editor.editor_conf as editor_conf


def register_plugin():
    editor_conf.register_function(pm.parent,
                                  None,
                                  {'Child': editor_conf.DataType.STRING,
                                   'Parent': editor_conf.DataType.STRING},
                                  nice_name='Parent')
