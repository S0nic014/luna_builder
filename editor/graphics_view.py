import imp
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.node_edge as node_edge
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.graphics_socket as graphics_socket
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.graphics_edge as graphics_edge
import luna_builder.editor.graphics_cutline as graphics_cutline
imp.reload(graphics_socket)


def history(description):
    def inner(func):
        def wrapper(*args, **kwargs):
            try:
                view = [a for a in args if isinstance(a, QLGraphicsView)][0]
            except IndexError:
                Logger.exception('Decorator failed to find QLGraphicsView in args')
                raise
            func(*args, **kwargs)
            view.scene.history.store_history(description)
            Logger.info('> {0}'.format(description))
        return wrapper
    return inner


class QLGraphicsView(QtWidgets.QGraphicsView):

    # Constant settings
    EDGE_DRAG_START_THRESHOLD = 10

    class EdgeMode(enumFn.Enum):
        NOOP = 1
        DRAG = 2
        CUT = 3

    def __init__(self, gr_scene, parent=None):
        super(QLGraphicsView, self).__init__(parent)

        self.gr_scene = gr_scene
        self.zoom_in_factor = 1.25
        self.zoom_clamp = False
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [0, 10]

        self.edge_mode = QLGraphicsView.EdgeMode.NOOP
        self.last_lmb_click_pos = None
        self.cutline = graphics_cutline.QLCutLine()
        self.gr_scene.addItem(self.cutline)

        self.init_ui()
        self.setScene(self.gr_scene)

    def init_ui(self):
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    @property
    def scene(self):
        return self.gr_scene.scene

    # =========== Qt Events overrides =========== #
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middle_mouse_press(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_mouse_press(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.right_mouse_press(event)
        else:
            super(QLGraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middle_mouse_release(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_mouse_release(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.right_mouse_release(event)
        else:
            super(QLGraphicsView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # Calculate zoom vector
        zoom_out_factor = 1 / self.zoom_in_factor

        # Calculate zoom
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom = self.zoom_range[0]
            clamped = True
        elif self.zoom > self.zoom_range[1]:
            self.zoom = self.zoom_range[1]
            clamped = True

        # Set scene scale
        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)

    def mouseMoveEvent(self, event):
        if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
            pos = self.mapToScene(event.pos())
            # Offset X to avoid clicking on the edge
            pos.setX(pos.x() - 1.0)
            if self.drag_edge.start_socket:
                self.drag_edge.gr_edge.set_destination(pos.x(), pos.y())
            else:
                self.drag_edge.gr_edge.set_source(pos.x(), pos.y())
            self.drag_edge.gr_edge.update()

        if self.edge_mode == QLGraphicsView.EdgeMode.CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()

        super(QLGraphicsView, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_selected()
        elif event.key() == QtCore.Qt.Key_Z and event.modifiers() & QtCore.Qt.ControlModifier and not event.modifiers() & QtCore.Qt.ShiftModifier:
            self.gr_scene.scene.history.undo()
        elif event.key() == QtCore.Qt.Key_Y and event.modifiers() & QtCore.Qt.ControlModifier and not event.modifiers() & QtCore.Qt.ShiftModifier:
            self.gr_scene.scene.history.redo()
        elif event.key() == QtCore.Qt.Key_H:
            Logger.debug(' len({0}) -- Current step: {1}'.format(len(self.scene.history), self.scene.history.current_step))
            for index, item in enumerate(self.scene.history.stack):
                Logger.debug('# {0} -- {1}'.format(index, item.get('desc')))

        else:
            super(QLGraphicsView, self).keyPressEvent(event)

    # =========== Handling button presses =========== #
    def middle_mouse_press(self, event):
        releaseEvent = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                         QtCore.Qt.LeftButton, QtCore.Qt.NoButton, event.modifiers())
        super(QLGraphicsView, self).mouseReleaseEvent(releaseEvent)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        fake_event = QtGui.QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                       QtCore.Qt.LeftButton, event.buttons() | QtCore.Qt.LeftButton, event.modifiers())
        super(QLGraphicsView, self).mousePressEvent(fake_event)

    def middle_mouse_release(self, event):
        fake_event = QtGui.QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                       QtCore.Qt.LeftButton, event.buttons() & ~QtCore.Qt.LeftButton, event.modifiers())
        super(QLGraphicsView, self).mouseReleaseEvent(fake_event)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    def left_mouse_press(self, event):

        item = self.get_item_at_click(event)
        # Store click position for future use
        self.last_lmb_click_pos = self.mapToScene(event.pos())

        # Handle socket click
        if isinstance(item, graphics_socket.QLGraphicsSocket):
            if self.edge_mode == QLGraphicsView.EdgeMode.NOOP:
                self.start_edge_drag(item)
                return

        if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
            result = self.end_edge_drag(item)
            if result:
                return

        if not item:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self.edge_mode = QLGraphicsView.EdgeMode.CUT
                fake_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                               QtCore.Qt.LeftButton, QtCore.Qt.NoButton, event.modifiers())
                super(QLGraphicsView, self).mouseReleaseEvent(fake_event)
                return

        super(QLGraphicsView, self).mousePressEvent(event)

    def left_mouse_release(self, event):
        item = self.get_item_at_click(event)

        if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
            if self.check_lmb_release_delta(event):
                result = self.end_edge_drag(item)
                if result:
                    return

        if self.edge_mode == QLGraphicsView.EdgeMode.CUT:
            self.cut_intersecting_edges()
            self.cutline.line_points = []
            self.cutline.update()
            self.edge_mode = QLGraphicsView.EdgeMode.NOOP
            return

        if self.dragMode() == QLGraphicsView.RubberBandDrag:
            self.scene.history.store_history('Selection changed')

        super(QLGraphicsView, self).mouseReleaseEvent(event)

    def right_mouse_press(self, event):
        super(QLGraphicsView, self).mousePressEvent(event)

        item = self.get_item_at_click(event)

        self.log_scene_objects(item)

    def right_mouse_release(self, event):
        super(QLGraphicsView, self).mouseReleaseEvent(event)

    # =========== Supporting methods =========== #
    def get_item_at_click(self, event):
        """Object at click event position

        :param event: Mouse click event
        :type event: QMouseEvent
        :return: Item clicked
        :rtype: QtWidgets.QGraphicsItem
        """
        item = self.itemAt(event.pos())  # type: QtWidgets.QGraphicsItem
        return item

    def check_lmb_release_delta(self, event):
        """Measures if LMB release position is greater then distance threshold.

        :param event: Left mouse click event
        :type event: QMouseEvent
        :return: Distance between clicked release positions is greater than threshold
        :rtype: bool
        """
        # Check if mouse was moved far enough from start socket and handle release if true
        new_lmb_releas_scene_pos = self.mapToScene(event.pos())
        click_release_delta = new_lmb_releas_scene_pos - self.last_lmb_click_pos
        return (click_release_delta.x() ** 2 + click_release_delta.y() ** 2) > QLGraphicsView.EDGE_DRAG_START_THRESHOLD ** 2

    def start_edge_drag(self, item):
        self.edge_mode = QLGraphicsView.EdgeMode.DRAG
        Logger.debug('Start dragging edge: {}'.format(self.edge_mode))
        Logger.debug('Assign socket to: {0}'.format(item.socket))
        if isinstance(item.socket, node_socket.OutputSocket):
            self.drag_edge = node_edge.Edge(self.gr_scene.scene, item.socket, None)
        else:
            self.drag_edge = node_edge.Edge(self.gr_scene.scene, None, item.socket)

    @history('Edge created by dragging')
    def end_edge_drag(self, item):
        self.edge_mode = QLGraphicsView.EdgeMode.NOOP
        Logger.debug('End dragging edge')
        if not isinstance(item, graphics_socket.QLGraphicsSocket) or not self.is_connection_possible(item):
            Logger.debug("Canceling edge dragging")
            self.drag_edge.remove()
            self.drag_edge = None
            return False

        # Another socket clicked while dragging edge
        if isinstance(item.socket, node_socket.OutputSocket):
            Logger.debug('Assign start socket: {0}'.format(item.socket))
            self.drag_edge.start_socket = item.socket
        elif isinstance(item.socket, node_socket.InputSocket):
            Logger.debug('Assign end socket: {0}'.format(item.socket))
            self.drag_edge.end_socket = item.socket

        # Set connections, update positions
        self.drag_edge.start_socket.set_connected_edge(self.drag_edge)
        self.drag_edge.end_socket.set_connected_edge(self.drag_edge)
        Logger.debug('Edge connected: {0}'.format(self.drag_edge))
        self.drag_edge.update_positions()
        return True

    def is_connection_possible(self, item):
        assigned_socket = self.drag_edge.get_assigned_socket()
        # Clicking on socket edge is dragging from
        if item.socket == assigned_socket:
            return False

        # Trying to connect output->output or input->input
        if isinstance(item.socket, type(assigned_socket)):
            Logger.warning('Can\'t connect two sockets of the same type')
            return False

        # Data types missmatch
        if item.socket.data_type != assigned_socket.data_type:
            Logger.warning('Can\'t connect data types {0} and {1}'.format(item.socket.data_type, assigned_socket.data_type))
            return False

        return True

    def log_scene_objects(self, item):
        if isinstance(item, graphics_socket.QLGraphicsSocket):
            Logger.debug(item.socket)
            Logger.debug('  Connected edge: {0}'.format(item.socket.edges))
        elif isinstance(item, graphics_node.QLGraphicsNode):
            Logger.debug(item.node)
        elif isinstance(item, graphics_edge.QLGraphicsEdge):
            Logger.debug(item.edge)
            Logger.debug('  Start: {0}, End:{1}'.format(item.edge.start_socket, item.edge.end_socket))

        if not item:
            Logger.debug('SCENE:')
            Logger.debug('  Nodes:')
            for node in self.gr_scene.scene.nodes:
                Logger.debug('    {0}'.format(node))
            Logger.debug('  Edges:')
            for edge in self.gr_scene.scene.edges:
                Logger.debug('    {0}'.format(edge))

    def debug_modifiers(self, event):
        """Helper function get string if we hold Ctrl, Shift or Alt modifier keys"""
        out = "MODS: "
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            out += "SHIFT "
        if event.modifiers() & QtCore.Qt.ControlModifier:
            out += "CTRL "
        if event.modifiers() & QtCore.Qt.AltModifier:
            out += "ALT "
        Logger.debug(out)

    @history('Item deleted')
    def delete_selected(self):
        selected_items = self.gr_scene.selectedItems()
        nodes_selected = [item for item in selected_items if isinstance(item, graphics_node.QLGraphicsNode)]
        if nodes_selected:
            for gr_node in nodes_selected:
                gr_node.node.remove()
        else:
            for item in selected_items:
                if isinstance(item, graphics_edge.QLGraphicsEdge):
                    item.edge.remove()

    @history('Edges cut')
    def cut_intersecting_edges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            pt1 = self.cutline.line_points[ix]
            pt2 = self.cutline.line_points[ix + 1]

            for edge in self.gr_scene.scene.edges:
                if edge.gr_edge.intersects_with(pt1, pt2):
                    edge.remove()
