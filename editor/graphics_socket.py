from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore

from luna import Logger


class QLGraphicsSocket(QtWidgets.QGraphicsItem):
    def __init__(self, socket, label, color=QtGui.QColor("#FFFF7700")):
        self.socket = socket
        super(QLGraphicsSocket, self).__init__(socket.node.gr_node)

        self.label = label
        self.radius = 6.0
        self.outline_width = 1.0
        self._color_background = color if isinstance(color, QtGui.QColor) else QtGui.QColor(color)
        self._color_outline = QtGui.QColor("#FF000000")

        # Pen, brush
        self._pen = QtGui.QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QtGui.QBrush(self._color_background)

        # Add text label
        self.text_item = QtWidgets.QGraphicsTextItem(self.label, parent=self)
        self.text_item.setTextWidth(self.socket.get_label_width())
        if self.socket.node_position in [self.socket.Position.RIGHT_TOP, self.socket.Position.RIGHT_BOTTOM]:
            self.align_text_right()

    def paint(self, painter, option=None, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QtCore.QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width)
        )

    def align_text_right(self):
        fmt = QtGui.QTextBlockFormat()
        fmt.setAlignment(QtCore.Qt.AlignRight)
        cursor = self.text_item.textCursor()  # type: QtGui.QTextCursor
        cursor.select(QtGui.QTextCursor.Document)
        cursor.mergeBlockFormat(fmt)
        cursor.clearSelection()
        self.text_item.setTextCursor(cursor)
