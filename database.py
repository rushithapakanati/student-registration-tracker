import sqlite3
import os

DB_FILE = "students.db"

def init_db():
    """Initialize SQLite database with students table."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idno TEXT,
                name TEXT,
            branch TEXT,
            year INTEGER,
            semester INTEGER,
            subject TEXT,
            subject_code TEXT,
            type TEXT,
            oclass TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_connection():
    """Return SQLite connection."""
    return sqlite3.connect(DB_FILE)

if __name__ == "__main__":
    init_db()