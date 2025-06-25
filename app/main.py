from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime
from app.db import insert_post, update_post_status, get_all_posts_by_status, get_all_pending_posts
from app.insta_client import login_and_save
import sqlite3
from app.models.image_generation import generate_image_and_upscale
from app.models.captioning import generate_caption, generate_hashtags


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

@main.route('/upload_image_caption', methods=['POST'])
def upload_image_caption():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    file = request.files.get('file')
    if not file:
        flash('Kein Datei-Upload erkannt.', 'danger')
        return redirect(url_for('main.dashboard'))

    path = save_uploaded_file(file)
    caption = request.form.get('caption')
    hashtags = request.form.get('hashtags')
    scheduled_time = normalize_scheduled_time(request.form.get('scheduled_time'))
    print(f"DEBUG UPLOAD: Caption='{caption}', Hashtags='{hashtags}'")
    insert_post(session['username'], path, caption, hashtags, 'image_caption', scheduled_time)
    flash("Bild + Caption erfolgreich eingeplant!" if scheduled_time else "Bild + Caption erfolgreich hochgeladen!", 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/upload_video', methods=['POST'])
def upload_video():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    file = request.files.get('file')
    if not file:
        flash('Kein Datei-Upload erkannt.', 'danger')
        return redirect(url_for('main.dashboard'))

    path = save_uploaded_file(file)
    caption = request.form.get('caption')
    hashtags = request.form.get('hashtags')
    scheduled_time = normalize_scheduled_time(request.form.get('scheduled_time'))
    insert_post(session['username'], path, caption, hashtags, 'video', scheduled_time)
    flash("Video erfolgreich eingeplant!" if scheduled_time else "Video erfolgreich hochgeladen!", 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/generate_image', methods=['POST'])
def generate_image():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    prompt = request.form.get('prompt')
    if not prompt:
        flash('Bitte einen Prompt eingeben.', 'danger')
        return redirect(url_for('main.dashboard'))

    filename_base = datetime.now().strftime("%Y%m%d%H%M%S")
    _, _, upload_path = generate_image_and_upscale(prompt, filename_base)
    rel_path = upload_path.replace("app/static/", "")

    return render_template('approve_generated.html', image_path=rel_path, prompt=prompt)

@main.route('/approve_generated_image', methods=['POST'])
def approve_generated_image():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    image_path = "app/static/" + request.form.get('image_path')
    caption = request.form.get('caption')
    hashtags = request.form.get('hashtags')
    scheduled_time = normalize_scheduled_time(request.form.get('scheduled_time'))

    insert_post(session['username'], image_path, caption, hashtags, 'image', scheduled_time)
    flash("KI-Bild erfolgreich übernommen!", 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/cancel_generated_image', methods=['POST'])
def cancel_generated_image():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    image_path = "app/static/" + request.form.get('image_path')

    # Datei löschen, wenn sie existiert
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            flash("Generiertes Bild wurde verworfen und gelöscht.", "info")
        else:
            flash("Datei nicht gefunden zum Löschen.", "warning")
    except Exception as e:
        flash(f"Fehler beim Löschen: {e}", "danger")

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

    
    if post[7] == 'posted':
        flash(f'Post {post_id} wurde bereits gepostet.', 'warning')
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

@main.route('/generate_blip_caption', methods=['POST'])
def generate_blip_caption():
    if not session.get('logged_in'):
        return jsonify({'error': 'Nicht eingeloggt'}), 401

    # Prüfen, ob ein Pfad übergeben wurde
    image_path = request.json.get('image_path') if request.is_json else None

    if image_path:
        full_path = os.path.join('app/static', image_path)
        if not os.path.exists(full_path):
            return jsonify({'error': 'Bild nicht gefunden'}), 400
    else:
        # Fallback: Datei-Upload
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'Kein Bild übermittelt'}), 400

        full_path = os.path.join(UPLOAD_FOLDER, "temp_" + datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename)
        file.save(full_path)
        delete_after = True
    try:
        caption = generate_caption(full_path)
    except Exception as e:
        if image_path is None and os.path.exists(full_path):
            os.remove(full_path)
        return jsonify({'error': f'Caption-Generierung fehlgeschlagen: {e}'}), 500

    if image_path is None and os.path.exists(full_path):
        os.remove(full_path)

    return jsonify({'caption': caption})


@main.route('/generate_blip_hashtags', methods=['POST'])
def generate_blip_hashtags():
    if not session.get('logged_in'):
        return jsonify({'error': 'Nicht eingeloggt'}), 401

    image_path = request.json.get('image_path') if request.is_json else None

    if image_path:
        full_path = os.path.join('app/static', image_path)
        if not os.path.exists(full_path):
            return jsonify({'error': 'Bild nicht gefunden'}), 400
    else:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'Kein Bild übermittelt'}), 400

        full_path = os.path.join(UPLOAD_FOLDER, "temp_" + datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename)
        file.save(full_path)

    try:
        hashtags = generate_hashtags(full_path)
    except Exception as e:
        if image_path is None and os.path.exists(full_path):
            os.remove(full_path)
        return jsonify({'error': f'Hashtag-Generierung fehlgeschlagen: {e}'}), 500

    if image_path is None and os.path.exists(full_path):
        os.remove(full_path)

    return jsonify({'hashtags': hashtags})