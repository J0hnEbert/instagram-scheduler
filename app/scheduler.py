import time
import threading
from app.db import get_due_posts, update_post_status, get_all_pending_posts
from app.insta_client import get_client

def post_now(post):
    post_id, username, file_path, caption, hashtags, post_type, scheduled_time, status = post
    cl = get_client(username)
    if not cl:
        raise Exception(f"Keine gültige Session für {username}. Bitte erneut einloggen.")

    full_caption = (caption or "") + "\n" + (hashtags or "")
    full_caption = full_caption.strip()

    if post_type == 'image':
        cl.photo_upload(file_path, "")
    elif post_type == 'image_caption':
        cl.photo_upload(file_path, full_caption)
    elif post_type == 'video':
        cl.video_upload(file_path, full_caption)
    else:
        raise Exception(f"Unbekannter Typ: {post_type}")

def scheduler_loop():
    print("[Scheduler] Gestartet...")
    while True:
        due_posts = get_due_posts()
        if due_posts:
            print(f"[Scheduler] Fällige Posts: {len(due_posts)}")
            for post in due_posts:
                try:
                    update_post_status(post[0], 'processing')
                    post_now(post)
                    update_post_status(post[0], 'posted')
                    print(f"[Scheduler] Post {post[0]} erfolgreich gepostet.")
                except Exception as e:
                    update_post_status(post[0], 'failed')
                    print(f"[Scheduler] Fehler bei Post {post[0]}: {e}")
        else:
            all_pending = get_all_pending_posts()
            if all_pending:
                print(f"[Scheduler] Nächster geplanter Post um: {all_pending[0][6]}")
            else:
                print("[Scheduler] Keine geplanten Posts.")
        time.sleep(10)
