from PySide2 import QtCore
from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.editor.node_serializable as node_serializable


class VarsSignals(QtCore.QObject):
    value_changed = QtCore.Signal(str)


class SceneVars(node_serializable.Serializable):
    def __init__(self, scene):
        super(SceneVars, self).__init__()
        self.scene = scene
        self.signals = VarsSignals()
        self._vars = {'test': (2.0, editor_conf.DataType.NUMERIC)}
        self.create_connections()

    def create_connections(self):
        self.signals.value_changed.connect(self.update_getters)

    def set_var(self, name, value, datatype):
        self._vars[name] = (value, datatype)
        self.signals.value_changed.emit(name)

    def update_getters(self, var_name):
        Logger.debug('Updating getters...')
        for getter_node in {node for node in self.scene.nodes if node.ID == editor_conf.GET_NODE_ID and node.var_name == var_name}:
            Logger.debug('   > Updating {0}'.format(getter_node))
            if not getter_node.out_value.data_type == self.get_data_type(var_name):
                getter_node.out_value.data_type = self.get_data_type(var_name)

            getter_node.out_value.value = self.get_value(var_name)

    def get_value(self, name):
        return self._vars[name][0]

    def get_data_type(self, name):
        return self._vars[name][1]

    def serialize(self):
        return {}

    def deserialize(self, data, hashmap={}):
        super(SceneVars, self).deserialize(data, hashmap=hashmap)
