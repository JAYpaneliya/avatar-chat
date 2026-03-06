import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "avatar_chat.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avatars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            location TEXT,
            relationship TEXT NOT NULL,
            situation TEXT,
            occupation TEXT,
            interests TEXT,
            behaviour TEXT,
            communication_style TEXT NOT NULL,
            slangs TEXT,
            language TEXT DEFAULT 'English',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            avatar_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (avatar_id) REFERENCES avatars(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")