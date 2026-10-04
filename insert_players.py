import sqlite3

conn = sqlite3.connect("cricket.db")
cursor = conn.cursor()

players_data = [
    ("Kohli", 102, 98, 8, 2, 0, 0, 0, 0, 1, 0, 0, 120, 189, 8257, 28, 43, "BAT"),
    ("Yuvraj", 12, 20, 1, 0, 48, 0, 36, 1, 0, 0, 0, 100, 86, 3589, 10, 21, "BAT"),
    ("Rahane", 49, 75, 1, 0, 0, 0, 0, 0, 1, 0, 0, 100, 158, 5435, 11, 31, "BAT"),
    ("Dhawan", 32, 35, 4, 0, 0, 0, 0, 0, 0, 0, 0, 85, 25, 565, 2, 1, "AR"),
    ("Dhoni", 56, 45, 3, 1, 0, 0, 0, 0, 3, 2, 0, 75, 78, 2573, 0, 0, "BAT"),
    ("Axar", 8, 4, 2, 0, 2, 0, 0, 0, 0, 0, 0, 100, 67, 208, 0, 0, "BWL"),
    ("Pandya", 42, 36, 3, 3, 30, 0, 25, 0, 1, 0, 0, 75, 70, 77, 0, 0, "BWL"),
    ("Jadeja", 18, 10, 1, 0, 6, 0, 6, 0, 0, 0, 0, 85, 16, 216, 0, 0, "AR"),
    ("Kedar", 65, 60, 7, 0, 24, 0, 24, 2, 0, 0, 0, 90, 11, 675, 0, 0, "BWL"),
    ("Ashwin", 23, 42, 3, 1, 30, 0, 20, 0, 1, 0, 0, 100, 136, 2914, 0, 10, "AR"),
    ("Umesh", 0, 0, 0, 0, 60, 0, 36, 1, 0, 0, 0, 110, 296, 9496, 10, 64, "BWL"),
    ("Bumrah", 0, 0, 0, 0, 60, 2, 49, 1, 0, 0, 0, 60, 73, 1365, 0, 8, "WK"),
    ("Bhuvneshwar", 15, 12, 2, 0, 60, 0, 36, 1, 0, 0, 0, 75, 17, 289, 0, 0, "AR"),
    ("Rohit", 46, 65, 5, 1, 0, 0, 0, 0, 0, 0, 0, 85, 304, 8701, 14, 52, "BAT"),
    ("Kartick", 29, 42, 3, 0, 0, 0, 0, 0, 2, 0, 1, 75, 11, 111, 0, 0, "AR"),
]

for p in players_data:
    cursor.execute("""
        INSERT INTO match (player, scored, faced, four, sixes, bowled, maiden, given, wkts, catches, stumping, ro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, p[:12])

    cursor.execute("""
        INSERT INTO stats (player, matches, run, "100s", "50s", value, ctg)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (p[0], p[13], p[14], p[15], p[16], p[12], p[17]))

conn.commit()
conn.close()

print("Player data inserted into match and stats tables successfully.")
