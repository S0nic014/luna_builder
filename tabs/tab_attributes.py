from luna import Logger
from PySide2 import QtWidgets


class AttributesEditor(QtWidgets.QWidget):
    def __init__(self, main_window, parent=None):
        super(AttributesEditor, self).__init__(parent)
        self.main_window = main_window
        self._current_widget = None  # type: QtWidgets.QWidget

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    @property
    def current_widget(self):
        return self._current_widget

    @current_widget.setter
    def current_widget(self, widget):
        self.clear_layout()
        self._current_widget = widget
        self.main_layout.addWidget(self._current_widget)
        self._current_widget.show()

    def update_current_widget(self):
        if not self.main_window.current_editor:
            return

        selected = self.main_window.current_editor.scene.selected_nodes
        if not selected:
            return

        node = selected[-1]
        widget = node.INSPECTOR_WIDGET(node)
        self.current_widget = widget

    def clear_layout(self):
        if self.current_widget:
            self.current_widget.close()
            self.current_widget.deleteLater()
            self.main_layout.removeWidget(self.current_widget)
            self._current_widget = None
