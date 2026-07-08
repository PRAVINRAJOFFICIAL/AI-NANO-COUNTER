import sqlite3

def init_db():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()