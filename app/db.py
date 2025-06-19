import sqlite3
import os

DB_PATH = os.path.join("data", "posts.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            file_path TEXT NOT NULL,
            caption TEXT,
            hashtags TEXT,
            post_type TEXT NOT NULL,
            scheduled_time INTEGER,  -- jetzt integer epoch seconds
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

def insert_post(username, file_path, caption, hashtags, post_type, scheduled_time):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO posts (username, file_path, caption, hashtags, post_type, scheduled_time, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    ''', (username, file_path, caption, hashtags, post_type, scheduled_time))
    conn.commit()
    print(f"[DB] Neuer Post hinzugefügt: {file_path}, type={post_type}, time={scheduled_time}")
    conn.close()

def get_due_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM posts 
        WHERE status = 'pending' AND 
        (scheduled_time IS NULL OR scheduled_time <= strftime('%s','now'))
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_pending_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM posts WHERE status = 'pending' ORDER BY scheduled_time
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_posts_by_status(statuses):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    q = f"SELECT * FROM posts WHERE status IN ({','.join(['?']*len(statuses))}) ORDER BY id DESC"
    c.execute(q, statuses)
    rows = c.fetchall()
    conn.close()
    return rows

def update_post_status(post_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE posts SET status = ? WHERE id = ?', (status, post_id))
    conn.commit()
    conn.close()
