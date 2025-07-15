class BookingNode:
    def __init__(self,ticket):
        self.ticket = ticket
        self.next = None
class BookingHistory:
    def __init__(self):
        self.head = None
    def add_booking(self,name,movie,seat):
        ticket = (name,movie,seat)
        new_node = BookingNode(ticket)
        new_node.next = self.head
        self.head = new_node
    def get_history_text(self):
        history = []
        current = self.head
        while current:
            name, movie, seat = current.ticket
            history.append(f"{name} booked{seat} in {movie}")
            current = current.next
        return "\n".join(history) if history else "No bookings yet"