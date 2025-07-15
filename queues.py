from collections import deque

class WaitingQueue:
    def _init_(self):
        self.queue = deque()

    def enqueue(self, name):
        self.queue.append(name)

    def get_waiting_list_text(self):
        return "\n".join(self.queue) if self.queue else "No one in waiting list."