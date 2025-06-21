import time
from app.db import get_due_posts, update_post_status
from app.insta_client import get_client

def post_now(post):
    cl = get_client(post[1])
    file_path = post[2]
    caption_text = (post[3] or '').strip()
    hashtags_text = (post[4] or '').strip()

    full_caption = caption_text
    if hashtags_text:
        if caption_text:
            full_caption += "\n" + hashtags_text
        else:
            full_caption = hashtags_text

    print(f"[DEBUG POST_NOW] Post ID: {post[0]}")
    print(f"[DEBUG POST_NOW] File: {file_path}")
    print(f"[DEBUG POST_NOW] Caption to send: {repr(full_caption)}")

    if post[5] in ['image', 'image_caption']:
        cl.photo_upload(path=file_path, caption=full_caption)
    elif post[5] == 'video':
        cl.video_upload(path=file_path, caption=full_caption)


def scheduler_loop():
    while True:
        due_posts = get_due_posts()
        if due_posts:
            print(f"[Scheduler] Fällige Posts gefunden: {len(due_posts)}")
        else:
            print("[Scheduler] Keine fälligen Posts.")

        for post in due_posts:
            print(f"[DEBUG] Post ID: {post[0]}")
            print(f"[DEBUG] File: {post[2]}")
            print(f"[DEBUG] Caption: {post[3]}")
            print(f"[DEBUG] Hashtags: {post[4]}")
            try:
                post_now(post)
                update_post_status(post[0], 'posted')
                print(f"[Scheduler] Post {post[0]} erfolgreich gepostet.")
            except Exception as e:
                update_post_status(post[0], 'failed')
                print(f"[Scheduler] Fehler beim Posten von {post[0]}: {e}")

        time.sleep(20)
