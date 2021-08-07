import timeit
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
        self.reset_nodes_compiled_state()
        result = self.verify_graph()
        if not result:
            Logger.warning('Invalid graph, execution canceled')
            return

        Logger.info('Initiating new build...')
        start_time = timeit.default_timer()
        input_node = self.find_input_node()
        if not input_node:
            return
        # Execute
        try:
            self.scene.is_executing = True
            input_node._exec()
            Logger.info("Build finished in {0:.2f}s".format(timeit.default_timer() - start_time))
        except Exception:
            self.scene.is_executing = False

    def reset_nodes_compiled_state(self):
        for node in self.scene.nodes:
            node._is_compiled = False

    def verify_graph(self):
        Logger.info('Verifing graph...')
        invalid_nodes = []
        for node in self.scene.nodes:
            result = node.verify()
            if not result:
                node.set_invalid(True)
                invalid_nodes.append(node)
        if invalid_nodes:
            for node in invalid_nodes:
                Logger.warning('Invalid node: {0}'.format(node.title))
            return False

        return True
