import sqlite3

conn = sqlite3.connect("cricket.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS match (
    player TEXT,
    scored INTEGER,
    faced INTEGER,
    four INTEGER,
    sixes INTEGER,
    bowled INTEGER,
    maiden INTEGER,
    given INTEGER,
    wkts INTEGER,
    catches INTEGER,
    stumping INTEGER,
    ro INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    name TEXT,
    players TEXT,
    value INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    player TEXT,
    matches INTEGER,
    run INTEGER,
    "100s" INTEGER,
    "50s" INTEGER,
    value INTEGER,
    ctg TEXT
);
""")

conn.commit()
conn.close()

print("Database and tables created successfully.")
