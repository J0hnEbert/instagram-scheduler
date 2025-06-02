import sqlite3
import os

DB_PATH = os.path.join("data", "posts.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            type TEXT,
            filename TEXT,
            caption TEXT,
            hashtags TEXT,
            schedule_time TEXT,
            timezone TEXT,
            posted INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_post_to_db(username, post_type, filename, caption, hashtags, schedule_time, timezone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (username, type, filename, caption, hashtags, schedule_time, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, post_type, filename, caption, hashtags, schedule_time, timezone))
    conn.commit()
    conn.close()

