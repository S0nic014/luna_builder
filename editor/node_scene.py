import imp
import timeit
from collections import OrderedDict

from luna import Logger
import luna.utils.fileFn as fileFn
import luna_builder.editor.node_node as node_node
import luna_builder.editor.node_edge as node_edge
import luna_builder.editor.graphics_scene as graphics_scene
import luna_builder.editor.node_serializable as node_serializable
import luna_builder.editor.node_scene_history as scene_history
imp.reload(scene_history)
imp.reload(graphics_scene)


class Scene(node_serializable.Serializable):

    def __init__(self):
        super(Scene, self).__init__()
        self.nodes = []
        self.edges = []
        self.gr_scene = None  # type: graphics_scene.QLGraphicsScene

        self.scene_width = 64000
        self.scene_height = 64000
        self.edge_type = node_edge.Edge.Type.BEZIER

        self.init_ui()
        self.history = scene_history.SceneHistory(self)

    def init_ui(self):
        self.gr_scene = graphics_scene.QLGraphicsScene(self)
        self.gr_scene.set_scene_size(self.scene_width, self.scene_height)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node):
        self.nodes.remove(node)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def selected_nodes(self):
        return [node for node in self.nodes if node.gr_node.isSelected()]

    def clear(self):
        while(self.nodes):
            self.nodes[0].remove()

    def save_to_file(self, file_path):
        try:
            fileFn.write_json(file_path, data=self.serialize(), sort_keys=False)
            Logger.info('Saved build {0}'.format(file_path))
        except Exception:
            Logger.exception('Failed to save build')

    def load_from_file(self, file_path):
        try:
            start_time = timeit.default_timer()
            data = fileFn.load_json(file_path)
            self.deserialize(data)
            Logger.info("Rig build loaded in {0:.2f}s".format(timeit.default_timer() - start_time))
        except Exception:
            Logger.exception('Failed to load rig build file')

    def serialize(self):
        nodes, edges = [], []
        for n in self.nodes:
            nodes.append(n.serialize())

        for e in self.edges:
            edges.append(e.serialize())

        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges)
        ])

    def deserialize(self, data, hashmap={}):
        self.clear()

        # create nodes
        for node_data in data.get('nodes'):
            node_node.Node(self).deserialize(node_data, hashmap)

        # create edges
        for edge_data in data.get('edges'):
            node_edge.Edge(self, None, None).deserialize(edge_data, hashmap)
