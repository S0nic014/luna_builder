from PySide2 import QtWidgets


class NodesPalette(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(NodesPalette, self).__init__('Nodes Palette', parent)

        self.setMinimumWidth(150)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # TODO: Replace with actual node items
        self.add_test_items()

    def create_widgets(self):
        self.nodes_list = QtWidgets.QListWidget()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.nodes_list)

    def create_connections(self):
        pass

    def add_test_items(self):
        self.nodes_list.addItems(['FKIK Component', 'FK Component', 'Spine Component', 'Foot Component'])
