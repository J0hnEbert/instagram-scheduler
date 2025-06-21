import sqlite3

DB_PATH = "data/posts.db"

def show_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, file_path, caption, hashtags, post_type, scheduled_time, status FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        print(f"ID: {row[0]}")
        print(f"User: {row[1]}")
        print(f"File: {row[2]}")
        print(f"Caption: {row[3]}")
        print(f"Hashtags: {row[4]}")
        print(f"Type: {row[5]}")
        print(f"Scheduled: {row[6]}")
        print(f"Status: {row[7]}")
        print("-" * 40)

if __name__ == "__main__":
    show_posts()
