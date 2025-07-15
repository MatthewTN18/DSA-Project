import database

class MovieManager:
    def get_movies(self):
        return ["Avengers", "Barbie", "Oppenheimer", "Mission Impossible: The Final Reckoning", "Straw", "Final Destination", "Eternals"]

    def get_movie_info(self, movie):
        info = {
            "Avengers": {"screen": "F1", "time": "9:00 AM"},
            "Barbie": {"screen": "F5", "time": "11:40 AM"},
            "Oppenheimer": {"screen": "F7", "time": "3:30 PM"},
            "Mission Impossible: The Final Reckoning": {"screen": "F3", "time": "6:15 PM"},
            "Straw": {"screen": "F2", "time": "8:00 AM"},
            "Final Destination": {"screen": "F6", "time": "12:30 PM"},
            "Eternals": {"screen": "F4", "time": "2:15 PM"}
        }
        return info.get(movie, {"screen": "TBD", "time": "TBD"})

    def get_seats(self, movie):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT seat FROM seats WHERE movie=%s AND status='available'", (movie,))
            results = [row[0] for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print("Error loading seats:", e)
            return []

    def book_seat(self, movie, seat):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM seats WHERE movie=%s AND seat=%s", (movie, seat))
            result = cursor.fetchone()
            if result and result[0] == "available":
                cursor.execute("UPDATE seats SET status='booked' WHERE movie=%s AND seat=%s", (movie, seat))
                conn.commit()
                return True
            return False
        except Exception as e:
            print("Error booking seat:", e)
            return False
        finally:
            conn.close()

    def restore_seat(self, movie, seat):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE seats SET status='available' WHERE movie=%s AND seat=%s", (movie, seat))
            conn.commit()
        except Exception as e:
            print("Error restoring seat:", e)
        finally:
            conn.close()
