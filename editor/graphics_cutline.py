from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLCutLine(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        super(QLCutLine, self).__init__(parent)

        self.line_points = []
        self._pen = QtGui.QPen(QtCore.Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, 1.0, 1.0)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QtGui.QPolygonF(self.line_points)
        painter.drawPolyline(poly)
