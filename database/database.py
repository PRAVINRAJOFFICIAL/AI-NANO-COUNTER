import sqlite3

conn = sqlite3.connect("analytics.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS detections (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    image_name TEXT,

    object_name TEXT,

    object_count INTEGER,

    total_objects INTEGER,

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()
conn.close()

print("Analytics Database Created Successfully")