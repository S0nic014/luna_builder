import math
from luna import Logger
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLGraphicsNode(QtWidgets.QGraphicsItem):

    def __init__(self, node, parent=None):
        super(QLGraphicsNode, self).__init__(parent)
        self.node = node

        # Init flags
        self._was_moved = False

        self.init_sizes()
        self.init_assets()

        self.init_ui()

    def init_ui(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self.init_title()
        self.title = self.node.title
        self.init_sockets()
        self.init_content()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    @property
    def width(self):
        return self.node.SIZE[0]

    @property
    def height(self):
        return self.node.SIZE[1]

    @property
    def title_height(self):
        return self.node.TITLE_HEIGHT

    def init_sizes(self):
        self.edge_size = 10.0
        self._padding = 4.0

    def init_assets(self):
        # Fonts colors
        self._title_color = QtCore.Qt.white
        self._title_font = QtGui.QFont("Arial", 10)

        # Pens, Brushes
        self._pen_default = QtGui.QPen(QtGui.QColor("#7F000000"))
        self._pen_selected = QtGui.QPen(QtGui.QColor("#FFA637"))
        self._brush_title = QtGui.QBrush(QtGui.QColor("#FF313131"))
        self._brush_background = QtGui.QBrush(QtGui.QColor("#E3212121"))

    def init_title(self):
        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self._padding)

    def init_content(self):
        pass

    def init_sockets(self):
        pass

    def paint(self, painter, option, widget=None):
        # title
        path_title = QtGui.QPainterPath()
        path_title.setFillRule(QtCore.Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QtGui.QPainterPath()
        path_content.setFillRule(QtCore.Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        # TODO: Paint prominent outline if exec input is connected
        path_outline = QtGui.QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def boundingRect(self):
        return QtCore.QRectF(0,
                             0,
                             self.width,
                             self.height).normalized()

    # Events
    def mouseMoveEvent(self, event):
        super(QLGraphicsNode, self).mouseMoveEvent(event)
        for node in self.scene().scene.selected_nodes:
            node.update_connected_edges()
        self._was_moved = True

    def mouseReleaseEvent(self, event):
        super(QLGraphicsNode, self).mouseReleaseEvent(event)
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.store_history('Node moved', set_modified=True)
