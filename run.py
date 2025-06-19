from app import create_app
from app.db import init_db
from app.scheduler import scheduler_loop
import threading

app = create_app()
init_db()

def start_scheduler():
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    print("[Main] Scheduler Thread gestartet.")

start_scheduler()

if __name__ == '__main__':
    app.run(port=8081, debug=True)
