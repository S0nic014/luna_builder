from luna import Logger


class SceneHistory(object):

    def __len__(self):
        return len(self.stack)

    def __init__(self, scene):
        self.scene = scene

        self.enabled = True
        self.stack = []
        self.limit = 32
        self.current_step = -1

    def clear(self):
        self.stack = []
        self.current_step = -1

    def undo(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.restore_history()
        else:
            Logger.warning('No more steps to undo')

    def redo(self):
        if self.current_step + 1 < len(self.stack):
            self.current_step += 1
            self.restore_history()
        else:
            Logger.warning('No more steps to redo')

    def restore_history(self):
        # Logger.debug('Restoring history | \nStep: @{0} | Max: {1}'.format(self.current_step, len(self)))
        self.restore_stamp(self.stack[self.current_step])
        self.scene.has_been_modified = True

    def store_history(self, description, set_modified=True):
        if not self.enabled:
            return

        # Logger.debug('Storing history {0}| \nStep: @{1} | Max: {2}'.format(description, self.current_step, len(self)))
        # if the pointer (current_step) is not at the end of stack
        if self.current_step + 1 < len(self.stack):
            self.stack = self.stack[0:self.current_step + 1]

        # history is outside of the limits
        if self.current_step + 1 >= self.limit:
            self.stack = self.stack[1:]
            self.current_step -= 1

        hs = self.create_stamp(description)

        self.stack.append(hs)
        self.current_step += 1
        self.scene.has_been_modified = set_modified

    def create_stamp(self, description):
        sel_obj = {'nodes': [node.id for node in self.scene.selected_nodes()],
                   'edges': [edge.id for edge in self.scene.selected_edges()]}

        stamp = {
            'desc': description,
            'snapshot': self.scene.serialize(),
            'selection': sel_obj
        }

        return stamp

    def restore_stamp(self, stamp):
        self.scene.deserialize(stamp['snapshot'])

        # Restore selection
        for edge_id in stamp['selection']['edges']:
            for edge in self.scene.edges:
                if edge.id == edge_id:
                    edge.gr_edge.setSelected(True)
                    break

        for node_id in stamp['selection']['nodes']:
            for node in self.scene.nodes:
                if node.id == node_id:
                    node.gr_node.setSelected(True)
                    break
