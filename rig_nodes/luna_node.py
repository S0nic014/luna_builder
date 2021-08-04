
from PySide2 import QtCore
from PySide2 import QtGui
import luna.static.directories as directories
import luna_builder.editor.node_node as node_node
import luna_builder.editor.graphics_node as graphics_node


class LunaGraphicsNode(graphics_node.QLGraphicsNode):

    ICON_DRAW_ZOOM_LIMIT = 2

    def init_assets(self):
        super(LunaGraphicsNode, self).init_assets()
        self.status_icons = QtGui.QImage(directories.get_icon_path('status_icons.png'))

    def paint(self, painter, option, widget=None):
        super(LunaGraphicsNode, self).paint(painter, option, widget=widget)
        if self.node.scene.view.zoom < self.ICON_DRAW_ZOOM_LIMIT:
            return
        if self.node.STATUS_ICON:
            icon_offset = 24.0
            if self.node.is_dirty():
                icon_offset = 0.0
            if self.node.is_invalid():
                icon_offset = 48.0
            painter.drawImage(
                QtCore.QRectF(-13.0, -13.0, 24.0, 24.0),
                self.status_icons,
                QtCore.QRectF(icon_offset, 0, 24.0, 24.0)
            )


class LunaNode(node_node.Node):

    ID = None
    ICON = None
    STATUS_ICON = True
    DEFAULT_TITLE = 'Luna Node'
    UNIQUE = False
    CATEGORY = 'Utils'

    def __init__(self, scene, title=None, inputs=[], outputs=[]):
        super(LunaNode, self).__init__(scene, title=title, inputs=inputs, outputs=outputs)

    def init_inner_classes(self):
        self.gr_node = LunaGraphicsNode(self)

    def pre_deserilization(self, data):
        pass

    def post_deserilization(self, data):
        pass

    def serialize(self):
        data_dict = super(LunaNode, self).serialize()
        data_dict['node_id'] = self.__class__.ID
        return data_dict

    def deserialize(self, data, hashmap, restore_id):
        self.pre_deserilization(data)
        super(LunaNode, self).deserialize(data, hashmap=hashmap, restore_id=restore_id)
        self.post_deserilization(data)
