from PySide2 import QtWidgets
from luna import Logger
import luna_builder.editor.editor_conf as editor_conf


class GraphExecutor(object):
    def __init__(self, scene):
        self.scene = scene

    def find_input_node(self):
        input_nodes = [node for node in self.scene.nodes if node.ID == editor_conf.INPUT_NODE_ID]
        if not input_nodes:
            Logger.error('At least one input node is required!')
            return None
        elif len(input_nodes) > 1:
            Logger.warning('More than 1 input node in the scene. Only the first one added will be executed!')
        return input_nodes[0]

    def execute_graph(self):
        input_node = self.find_input_node()
        if not input_node:
            return
        input_node._exec()
