from luna import Logger
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLGraphicsTitle(QtWidgets.QGraphicsTextItem):

    EDIT_FLAGS = QtWidgets.QGraphicsItem.ItemIsFocusable

    def __init__(self, gr_node, text='', is_editable=False):
        super(QLGraphicsTitle, self).__init__(text, gr_node)
        self.gr_node = gr_node
        self.is_editable = is_editable
        self.default_flags = self.flags()
        self.previous_text = None
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

    def set_text_interaction(self, state, select_all=False, cursor_at_end=True):
        # Save previous text to compare later
        # Title is not in edit mode already and becomes editable
        if state and self.textInteractionFlags() == QtCore.Qt.NoTextInteraction:
            # Define starting text
            self.previous_text = self.toPlainText()
            if self.previous_text == self.gr_node.node.DEFAULT_TITLE:
                self.setPlainText('')

            # Set flags and focus
            self.setFlags(self.EDIT_FLAGS)
            self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
            # Set cursor
            self.setFocus(QtCore.Qt.MouseFocusReason)
            cursor = self.textCursor()  # type: QtGui.QTextCursor
            if cursor_at_end:
                cursor.movePosition(QtGui.QTextCursor.End)
            elif select_all:
                cursor.select(QtGui.QTextCursor.Document)
            self.setTextCursor(cursor)
        # Title is editable and becomes not editable
        elif not state and self.textInteractionFlags() == QtCore.Qt.TextEditorInteraction:
            self.setFlags(self.default_flags)
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.clearFocus()

    def apply_edit(self):
        new_text = self.toPlainText().strip()
        if new_text == self.previous_text:
            return
        self.gr_node.node.signals.title_edited.emit(new_text)

    def exit_editing(self):
        self.set_text_interaction(False)
        self.apply_edit()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.exit_editing()
            return

        super(QLGraphicsTitle, self).keyPressEvent(event)

    def focusOutEvent(self, event):
        self.exit_editing()
        super(QLGraphicsTitle, self).focusOutEvent(event)


class QLGraphicsNode(QtWidgets.QGraphicsItem):

    TEXT_ZOOM_OUT_LIMIT = 2

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
        self.init_content()

    @property
    def title(self):
        return self.title_item.toPlainText()

    @title.setter
    def title(self, value):
        self.title_item.setPlainText(value)

    @property
    def width(self):
        return self.node.max_width_of_socket_labels()

    @property
    def height(self):
        return self.node.max_height_of_sockets() + self.title_height + self.lower_padding

    @property
    def title_height(self):
        return self.node.TITLE_HEIGHT

    def init_sizes(self):
        self.edge_roundness = 10.0
        self.edge_padding = 10.0
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = 4.0
        self.lower_padding = 8.0

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
        self.title_item = QLGraphicsTitle(self, is_editable=self.node.TITLE_EDITABLE)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def init_content(self):
        pass

    def paint(self, painter, option, widget=None):
        self.title_item.setVisible(self.node.scene.view.zoom > self.TEXT_ZOOM_OUT_LIMIT)

        # title
        path_title = QtGui.QPainterPath()
        path_title.setFillRule(QtCore.Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QtGui.QPainterPath()
        path_content.setFillRule(QtCore.Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.width - self.edge_roundness, self.title_height, self.edge_roundness, self.edge_roundness)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        # TODO: Paint prominent outline if exec input is connected
        path_outline = QtGui.QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_roundness, self.edge_roundness)
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
