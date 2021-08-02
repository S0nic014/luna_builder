
import luna_rig.importexport as import_export
import luna_builder.editor.editor_conf as editor_conf


def register_plugin():
    editor_conf.register_function(import_export.SkinManager.import_all,
                                  None,
                                  nice_name='Import Skin Weights',
                                  category='Data')
    editor_conf.register_function(import_export.NgLayers2Manager.import_all,
                                  None,
                                  nice_name='Import NgLayers2',
                                  category='Data')
    editor_conf.register_function(import_export.CtlShapeManager.import_asset_shapes,
                                  None,
                                  nice_name='Import Control Shapes',
                                  category='Data')
    editor_conf.register_function(import_export.BlendShapeManager.import_all,
                                  None,
                                  nice_name='Import BlendShapes',
                                  category='Data')
    editor_conf.register_function(import_export.DrivenPoseManager.import_all,
                                  None,
                                  nice_name='Import Driven Poses',
                                  category='Data')
    editor_conf.register_function(import_export.PsdManager.import_all,
                                  None,
                                  nice_name='Import PSD',
                                  category='Data')
    editor_conf.register_function(import_export.SDKCorrectiveManager.import_all,
                                  None,
                                  nice_name='Import SDK Correctives',
                                  category='Data')
