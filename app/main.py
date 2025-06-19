from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime
from app.db import insert_post, update_post_status, get_all_posts_by_status, get_all_pending_posts
from app.insta_client import login_and_save, get_client
import sqlite3

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'app/static/uploads'

def save_uploaded_file(file):
    filename = datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(path)
    return path

def normalize_scheduled_time(raw_time):
    if not raw_time:
        return None
    try:
        dt = datetime.fromisoformat(raw_time)
        return int(dt.timestamp())
    except ValueError:
        return None

@main.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cl = login_and_save(username, password)
            session['logged_in'] = True
            session['username'] = username
            flash('Login erfolgreich!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash(f'Login fehlgeschlagen: {e}', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('Du wurdest ausgeloggt.', 'info')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    scheduled = get_all_pending_posts()
    completed = get_all_posts_by_status(['posted', 'failed'])
    return render_template('dashboard.html', scheduled_posts=scheduled, completed_posts=completed)

@main.route('/upload_image', methods=['POST'])
def upload_image():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    file = request.files.get('file')
    if not file:
        flash('Kein Datei-Upload erkannt.', 'danger')
        return redirect(url_for('main.dashboard'))

    path = save_uploaded_file(file)
    scheduled_time = normalize_scheduled_time(request.form.get('scheduled_time'))
    insert_post(session['username'], path, None, None, 'image', scheduled_time)
    flash("Bild erfolgreich eingeplant!" if scheduled_time else "Bild erfolgreich hochgeladen!", 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/trigger_post/<int:post_id>')
def trigger_post(post_id):
    conn = sqlite3.connect('data/posts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()

    if not post:
        flash('Post nicht gefunden.', 'danger')
        return redirect(url_for('main.dashboard'))

    try:
        from app.scheduler import post_now
        post_now(post)
        update_post_status(post_id, 'posted')
        flash(f'Post {post_id} wurde manuell gepostet.', 'success')
    except Exception as e:
        update_post_status(post_id, 'failed')
        flash(f'Fehler beim manuellen Posten: {e}', 'danger')

    return redirect(url_for('main.dashboard'))

@main.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    conn = sqlite3.connect('data/posts.db')
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash(f'Post {post_id} wurde gelöscht.', 'info')
    return redirect(url_for('main.dashboard'))
