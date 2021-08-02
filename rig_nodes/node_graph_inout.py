
import pymel.core as pm
import luna.workspace
from luna import Logger
import luna_rig.functions.asset_files as asset_files
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class GraphInputNode(luna_node.LunaNode):
    ID = editor_conf.INPUT_NODE_ID
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    ICON = 'input.png'
    DEFAULT_TITLE = 'Input'
    CATEGORY = 'Utils'
    UNIQUE = True

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        self.exec_in_socket = None
        self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC)
        self.out_asset_name = self.add_output(editor_conf.DataType.STRING, label='Asset Name', value='')

    def execute(self):
        if not luna.workspace.Asset.get():
            Logger.error('Asset is not set!')
            return 1

        try:
            self.out_asset_name.value = luna.workspace.Asset.get().name
            pm.newFile(f=1)
            asset_files.import_model()
            asset_files.import_skeleton()
        except Exception:
            Logger.exception('Failed to initialize build')
            return 1
        return 0


class GraphOutputNode(luna_node.LunaNode):
    ID = editor_conf.OUTPUT_NODE_ID
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    ICON = 'output.png'
    DEFAULT_TITLE = 'Output'
    CATEGORY = 'Utils'
    UNIQUE = True

    def init_sockets(self, inputs=[], outputs=[], reset=True):
        self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
        self.exec_out_socket = None


def register_plugin():
    editor_conf.register_node(GraphInputNode.ID, GraphInputNode)
    editor_conf.register_node(GraphOutputNode.ID, GraphOutputNode)
