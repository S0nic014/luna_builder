import itertools
from collections import deque
from luna import Logger


class SceneHistory(object):

    def __len__(self):
        return len(self.stack)

    def __init__(self, scene):
        self.scene = scene
        self.stack = deque(maxlen=8)
        self.current_step = -1

    def undo(self):
        if self.current_step < 0:
            Logger.warning('No more steps to undo')
            return

        Logger.debug('UNDO')
        self.current_step -= 1
        self.restore_history()

    def redo(self):
        if self.current_step + 1 == len(self.stack):
            Logger.warning('No more steps to redo')
            return

        Logger.debug('REDO')
        self.current_step += 1
        self.restore_history()

    def restore_history(self):
        Logger.debug('Restoring history | \nStep: @{0} | Max: {1}'.format(self.current_step, len(self)))
        self.restore_stamp(self.stack[self.current_step])

    def store_history(self, description):
        Logger.debug('Storing history {0}| \nStep: @{1} | Max: {2}'.format(description, self.current_step, len(self)))

        if self.current_step + 1 < len(self.stack):
            self.stack = deque(itertools.islice(self.stack, self.current_step + 1), maxlen=self.stack.maxlen)

        hs = self.create_stamp(description)
        self.stack.append(hs)
        if self.current_step + 1 != self.stack.maxlen:
            self.current_step += 1
        Logger.debug('Max step: {0}'.format(self.current_step))

    def restore_stamp(self, stamp):
        Logger.debug('Stamp: {0}'.format(stamp))

    def create_stamp(self, description):
        return description
