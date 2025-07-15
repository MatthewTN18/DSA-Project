class UndoStack:
    def __init__(self):
        self.stack = []

    def push(self, movie, seat):
        self.stack.append((movie, seat))

    def undo_last(self, manager):
        if not self.stack:
            return None
        movie, seat = self.stack.pop()
        manager.restore_seat(movie, seat)
        return movie, seat