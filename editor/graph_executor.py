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

    def validate_graph(self):
        return True

    def execute_graph(self):
        result = self.validate_graph()
        if not result:
            return
        for node in self.execution_chain():
            Logger.debug('Executing {0}...'.format(node))
            result = node.execute()
            if result:
                node.set_invalid(True)
                break
            else:
                node.set_dirty(False)
                node.set_invalid(False)

    def execution_chain(self):
        input_node = self.find_input_node()
        if not input_node:
            return []

        chain = [input_node]
        for child in input_node.list_exec_children():
            chain.append(child)
            chain += child.list_exec_children()

        return chain

    def debug_execution_chain(self):
        for node in self.execution_chain():
            Logger.debug(node)
