from instagrapi import Client
import os

SESSIONS_DIR = "data/sessions"

def _session_file(username):
    return os.path.join(SESSIONS_DIR, f"{username}.json")

def login_and_save(username, password):
    cl = Client()
    cl.login(username, password)

    os.makedirs(SESSIONS_DIR, exist_ok=True)
    cl.dump_settings(_session_file(username))
    cl.get_timeline_feed()  
    return cl

def get_client(username):
    cl = Client()
    session_path = _session_file(username)

    if os.path.exists(session_path):
        try:
            cl.load_settings(session_path)
            cl.get_timeline_feed()  
            return cl
        except Exception as e:
            print(f"[ERROR] Session für {username} ungültig: {e}")
            os.remove(session_path)

    return None
