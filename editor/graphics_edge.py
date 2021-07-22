from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLGraphicsEdge(QtWidgets.QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super(QLGraphicsEdge, self).__init__(parent)

        self.edge = edge
        self.source_position = [0, 0]
        self.destination_position = [200, 100]

        # Colors and pens
        self._color = QtGui.QColor("#001000")
        self._color_selected = QtGui.QColor("#00ff00")
        self._pen = QtGui.QPen(self._color)
        self._pen_selected = QtGui.QPen(self._color_selected)
        self._pen_dragging = QtGui.QPen(self._color)
        self._pen_dragging.setStyle(QtCore.Qt.DashLine)
        self._pen.setWidthF(2.0)
        self._pen_selected.setWidthF(3.0)
        self._pen_dragging.setWidthF(2.0)

        # Flags
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def set_source(self, x, y):
        self.source_position = [x, y]

    def set_destination(self, x, y):
        self.destination_position = [x, y]

    def paint(self, painter, widget=None, options=None):
        self.setPath(self.calc_path())

        if not self.edge.end_socket or not self.edge.start_socket:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(self.path())

    def calc_path(self):
        """Handle path drawing from point A to point B"""
        raise NotImplementedError("This method has to be overriden in a derived class")

    def intersects_with(self, pt1, pt2):
        cutpath = QtGui.QPainterPath(pt1)
        cutpath.lineTo(pt2)
        path = self.calc_path()
        return cutpath.intersects(path)

        return False


class QLGraphicsEdgeDirect(QLGraphicsEdge):
    def calc_path(self):
        path = QtGui.QPainterPath(QtCore.QPointF(*self.source_position))
        path.lineTo(*self.destination_position)
        return path


class QDGraphicsEdgeBezier(QLGraphicsEdge):
    def calc_path(self):
        distance = (self.destination_position[0] - self.source_position[0]) * 0.5
        if self.source_position[0] > self.destination_position[0]:
            distance *= -1
        ctl_point1 = [self.source_position[0] + distance, self.source_position[1]]
        ctl_point2 = [self.destination_position[0] - distance, self.destination_position[1]]

        path = QtGui.QPainterPath(QtCore.QPointF(*self.source_position))
        path.cubicTo(QtCore.QPointF(*ctl_point1), QtCore.QPointF(*ctl_point2), QtCore.QPointF(*self.destination_position))
        return path
