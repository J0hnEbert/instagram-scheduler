import time
import threading
from app.db import get_due_posts, update_post_status, get_all_pending_posts
from app.insta_client import get_client
import datetime

def post_now(post):
    post_id, username, file_path, caption, hashtags, post_type, scheduled_time, status = post
    cl = get_client(username)
    if not cl:
        raise Exception(f"Keine gültige Session für {username}. Bitte erneut einloggen.")

    full_caption = (caption or "") + "\n" + (hashtags or "")
    if post_type in ['image', 'image_caption']:
        cl.photo_upload(file_path, full_caption.strip())
    elif post_type == 'video':
        cl.video_upload(file_path, full_caption.strip())
    else:
        raise Exception(f"Unbekannter Typ: {post_type}")

def scheduler_loop():
    print("[Scheduler] Gestartet...")
    while True:
        due_posts = get_due_posts()
        if due_posts:
            print(f"[Scheduler] Fällige Posts: {len(due_posts)}")
        else:
            from app.db import get_all_pending_posts
            all_pending = get_all_pending_posts()
            if all_pending:
                print(f"[Scheduler] Nächster geplanter Post um: {all_pending[0][6]}")
            else:
                print("[Scheduler] Keine geplanten Posts.")

        for post in due_posts:
            try:
                # Verhindert Doppelbearbeitung sofort
                update_post_status(post[0], 'processing')
                post_now(post)
                update_post_status(post[0], 'posted')
                print(f"[Scheduler] Post {post[0]} erfolgreich gepostet.")
            except Exception as e:
                update_post_status(post[0], 'failed')
                print(f"[Scheduler] Fehler bei Post {post[0]}: {e}")
        time.sleep(30)

