import sqlite3
from app.config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        plate TEXT,
        violation_type TEXT,
        timestamp TEXT,
        hash TEXT,
        image_path TEXT
    )
    """)
    conn.commit()
    conn.close()
