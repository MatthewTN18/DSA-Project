import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from movie_manager import MovieManager
from linked_list import BookingHistory
from queue import WaitingQueue
from stack import UndoStack
import database
from tkinter import messagebox

#Global objects
manager = MovieManager()
history = BookingHistory()
waiting_list = WaitingQueue()
undo_stack = UndoStack()

class MovieBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Movie Booking System")
        self.root.geometry("1200x750")

        self.selected_movie = ttk.StringVar()
        self.selected_seat = ttk.StringVar()
        self.username = ttk.StringVar()
        self.payment_method = ttk.StringVar()
        self.seat_buttons = []

        self.create_layout()

    def create_layout(self):
        # Sidebar
        sidebar = ttk.Frame(self.root, bootstyle="light")
        sidebar.pack(side="left", fill="y", padx=(0, 10), pady=10)

        ttk.Label(sidebar, text="Menu", font=("Segoe UI", 14, "bold")).pack(pady=(10, 15))

        buttons = [
            ("Book Ticket", self.book_seat),
            ("View Bookings", self.view_all_bookings),
            ("Show History", self.show_history),
            ("Undo", self.undo),
            ("Waiting List", self.show_waiting)
        ]

        for (text, command) in buttons:
            ttk.Button(sidebar, text=text, bootstyle="primary-outline", width=20, command=command).pack(pady=5)

        # Main Content
        content = ttk.Frame(self.root, padding=20)
        content.pack(fill="both", expand=True)

        form = ttk.Frame(content)
        form.pack(anchor="nw", pady=10)

        ttk.Label(form, text="Your Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.username, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Select Movie:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        movie_menu = ttk.Combobox(form, textvariable=self.selected_movie, values=manager.get_movies(), width=28)
        movie_menu.grid(row=1, column=1, padx=5, pady=5)
        movie_menu.bind("<<ComboboxSelected>>", self.render_seat_grid)

        ttk.Label(form, text="Payment Method:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        payment_menu = ttk.Combobox(form, textvariable=self.payment_method,
                                    values=["Credit Card", "Mpesa", "Airtel Money"], width=28)
        payment_menu.grid(row=2, column=1, padx=5, pady=5)

        self.movie_info_label = ttk.Label(form, text="Select a movie to see screen & time", font=("Segoe UI", 10))
        self.movie_info_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 15))

        ttk.Label(content, text="💺 Seat Selection", font=("Segoe UI", 14, "bold")).pack(anchor="nw")
        self.seat_frame = ttk.Frame(content)
        self.seat_frame.pack(anchor="nw", pady=10)

        self.selected_label = ttk.Label(content, text="Selected Seat: None", font=("Segoe UI", 10))
        self.selected_label.pack(anchor="nw", pady=(0, 10))

        ttk.Label(content, text="💻 Log Console", font=("Segoe UI", 12, "bold")).pack(anchor="nw")
        self.log_box = ScrolledText(content, height=10, width=85, font=("Consolas", 10))
        self.log_box.pack()

    def render_seat_grid(self, _):
        for widget in self.seat_frame.winfo_children():
            widget.destroy()
        self.seat_buttons = []

        movie = self.selected_movie.get()
        movie_info = manager.get_movie_info(movie)
        self.movie_info_label.config(
            text=f"{movie} showing on screen {movie_info['screen']} at {movie_info['time']}"
        )

        available_seats = manager.get_seats(movie)
        all_seats = [chr(r)+str(c+1) for r in range(65, 69) for c in range(4)]  # A1-D4

        for index, seat in enumerate(all_seats):
            row = index // 4
            col = index % 4
            state = "disabled" if seat not in available_seats else "normal"
            style = "danger" if state == "disabled" else "success-outline"

            btn = ttk.Button(self.seat_frame, text=seat, width=6, bootstyle=style, state=state,
                             command=lambda s=seat: self.select_seat(s))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.seat_buttons.append(btn)

    def select_seat(self, seat):
        self.selected_seat.set(seat)
        self.selected_label.config(text=f"Selected Seat: {seat}")
        for btn in self.seat_buttons:
            if btn['text'] == seat:
                btn.configure(bootstyle="info")
            elif btn['state'] == "normal":
                btn.configure(bootstyle="success-outline")

    def log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def book_seat(self):
        name = self.username.get()
        movie = self.selected_movie.get()
        seat = self.selected_seat.get()
        payment = self.payment_method.get()

        if not name or not movie or not seat or not payment:
            messagebox.showwarning("Missing Info", "Please fill in all fields, including payment method")
            return

        if manager.book_seat(movie, seat):
            undo_stack.push(movie, seat)
            history.add_booking(name, movie, seat)
            self.log(f"✅ Booked: {seat} for {name} in {movie} via {payment}")

            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO bookings (name, movie, seat, payment) VALUES (%s, %s, %s, %s)",
                               (name, movie, seat, payment))
                conn.commit()
                conn.close()
            except Exception as e:
                self.log(f"❌ Database Error: {e}")
                return

            messagebox.showinfo("Success", f"Ticket booked:\n{name} - {movie} - {seat}\nPayment: {payment}")
            self.render_seat_grid(None)
        else:
            waiting_list.enqueue(name)
            self.log(f"⚠️ {name} added to waiting list (movie full)")
            messagebox.showinfo("Waiting List", f"{name} added to waiting list.")

    def undo(self):
        result = undo_stack.undo_last(manager)
        if result:
            movie, seat = result
            self.log(f"↩️ Undo: Restored seat {seat} in {movie}")
            self.render_seat_grid(None)
        else:
            messagebox.showinfo("Undo", "Nothing to undo.")

    def show_history(self):
        text = history.get_history_text()
        self.log("📚 Booking History:\n" + text)
        messagebox.showinfo("Booking History", text)

    def show_waiting(self):
        text = waiting_list.get_waiting_list_text()
        self.log("📋 Waiting List:\n" + text)
        messagebox.showinfo("Waiting List", text)

    def view_all_bookings(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, movie, seat, payment FROM bookings")
            results = cursor.fetchall()
            conn.close()

            if results:
                text = "\n".join([f"{row[0]} - {row[1]} - {row[2]} (Payment: {row[3]})" for row in results])
                self.log("📒 All Bookings:\n" + text)
                messagebox.showinfo("All Bookings", text)
            else:
                messagebox.showinfo("All Bookings", "No bookings found.")
        except Exception as e:
            self.log(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("Running Movie Booking App...")
    app = ttk.Window(themename="flatly")
    MovieBookingApp(app)
    app.mainloop()
