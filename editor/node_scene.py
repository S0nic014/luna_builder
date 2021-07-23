import imp
from collections import OrderedDict
from luna import Logger
import luna.utils.fileFn as fileFn
import luna_builder.editor.graphics_scene as graphics_scene
import luna_builder.editor.node_serializable as node_serializable
imp.reload(graphics_scene)


class Scene(node_serializable.Serializable):
    def __init__(self):
        super(Scene, self).__init__()
        self.nodes = []
        self.edges = []
        self.gr_scene = None  # type: graphics_scene.QLGraphicsScene

        self.scene_width = 64000
        self.scene_height = 64000

        self.init_ui()

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

    def save_to_file(self, file_path):
        try:
            fileFn.write_json(file_path, data=self.serialize(), sort_keys=False)
            Logger.info('Saved build {0}'.format(file_path))
        except Exception:
            Logger.exception('Failed to save build')

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

    def deserialize(self, data, hashmap):
        pass
