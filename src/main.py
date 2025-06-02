from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from db import init_db, save_post_to_db

app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/scheduler', methods=["GET", "POST"])
def scheduler():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")  # todo: implement login
        session["username"] = username
        return redirect(url_for("scheduler"))
    
    if "username" not in session:
        return redirect(url_for("index"))
    
    return render_template("scheduler.html", username=session["username"])

@app.route('/upload/<username>', methods=["POST"])
def upload_file(username):
    if "file" not in request.files:
        return jsonify({"status": "error", "error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "error": "Empty filename"}), 400
    
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    return jsonify({"status": "success", "filename": filename})

@app.route('/schedule', methods=["POST"])
def schedule():
    if "username" not in session:
        return jsonify({"status": "error", "error": "Unauthorized"}), 401

    username = session["username"]
    post_type = request.form.get("type")
    filename = request.form.get("filename")
    caption = request.form.get("caption", "")
    hashtags = request.form.get("hashtags", "")
    schedule_time = request.form.get("schedule_time")
    timezone = request.form.get("timezone")

    try:
        schedule_dt = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M")
    except Exception as e:
        return jsonify({"status": "error", "error": "Invalid datetime format"}), 400

    save_post_to_db(username, post_type, filename, caption, hashtags, schedule_dt.isoformat(), timezone)
    return jsonify({"status": "success", "message": "Post scheduled!"})

if __name__ == "__main__":
    app.run(debug=True, port=8081)
