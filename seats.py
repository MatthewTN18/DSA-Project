import database

def initialize_seats():
    movies = [
        "Avengers", "Barbie", "Oppenheimer",
        "Mission Impossible: The Final Reckoning",
        "Straw", "Final Destination", "Eternals",
        "Sonic 2", "Moana", "The Matrix"
    ]
    layout = [chr(r)+str(c+1) for r in range(65, 69) for c in range(4)]  # A1–D4

    conn = database.get_connection()
    cursor = conn.cursor()

    for movie in movies:
        for seat in layout:
            cursor.execute("SELECT * FROM seats WHERE movie=%s AND seat=%s", (movie, seat))
            result = cursor.fetchone()
            if not result:
                cursor.execute(
                    "INSERT INTO seats (movie, seat, status) VALUES (%s, %s, 'available')",
                    (movie, seat)
                )

    conn.commit()
    conn.close()

initialize_seats()