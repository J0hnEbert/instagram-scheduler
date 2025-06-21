import time
from app.db import get_due_posts, update_post_status
from app.insta_client import get_client

def post_now(post):
    cl = get_client(post[1])
    file_path = post[2]
    caption = (post[3] or '') + "\n" + (post[4] or '')
    if post[5] in ['image', 'image_caption']:
        cl.photo_upload(file_path, caption.strip())
    elif post[5] == 'video':
        cl.video_upload(file_path, caption.strip())

def scheduler_loop():
    while True:
        due_posts = get_due_posts()
        if due_posts:
            print(f"[Scheduler] Fällige Posts gefunden: {len(due_posts)}")
        else:
            print("[Scheduler] Keine fälligen Posts.")
        for post in due_posts:
            try:
                post_now(post)
                update_post_status(post[0], 'posted')
                print(f"[Scheduler] Post {post[0]} erfolgreich gepostet.")
            except Exception as e:
                update_post_status(post[0], 'failed')
                print(f"[Scheduler] Fehler beim Posten von {post[0]}: {e}")
        time.sleep(10)
