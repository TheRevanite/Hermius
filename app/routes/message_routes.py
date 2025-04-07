from flask import Blueprint, request, redirect, url_for, session, flash, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..database.db import get_db_connection  # Assumes this function exists
from functools import wraps

message_routes = Blueprint("message_routes", __name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --- Helper Functions ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("You must be logged in to perform this action.", "error")
            return redirect(url_for("auth_routes.login"))
        return f(*args, **kwargs)
    return decorated_function


# --- Routes ---

@message_routes.route("/messages/delete/<int:message_id>", methods=["POST"])
@login_required
def delete_message(message_id):
    conn = get_db_connection()
    c = conn.cursor()

    username = session["username"]
    message = c.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()

    if message and message["sender"] == username:
        c.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
        flash("Message deleted successfully.", "success")
    else:
        flash("You can only delete your own messages.", "error")

    conn.close()
    return redirect(request.referrer or url_for("main_routes.home"))


@message_routes.route("/messages/edit/<int:message_id>", methods=["POST"])
@login_required
def edit_message(message_id):
    new_content = request.form.get("edited_message")
    conn = get_db_connection()
    c = conn.cursor()

    username = session["username"]
    message = c.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()

    if message and message["sender"] == username:
        c.execute(
            "UPDATE messages SET content = ?, edited_at = ? WHERE id = ?",
            (new_content, datetime.utcnow(), message_id)
        )
        conn.commit()
        flash("Message edited successfully.", "success")
    else:
        flash("You can only edit your own messages.", "error")

    conn.close()
    return redirect(request.referrer or url_for("main_routes.home"))


@message_routes.route("/messages/report/<int:message_id>", methods=["POST"])
@login_required
def report_message(message_id):
    reason = request.form.get("reason", "No reason provided")
    conn = get_db_connection()
    c = conn.cursor()

    reporter = session["username"]
    c.execute(
        "INSERT INTO reports (message_id, reporter, reason, reported_at) VALUES (?, ?, ?, ?)",
        (message_id, reporter, reason, datetime.utcnow())
    )
    conn.commit()
    conn.close()
    flash("Message reported. Thank you for helping us keep Hermius safe.", "success")
    return redirect(request.referrer or url_for("main_routes.home"))


@message_routes.route("/media/upload", methods=["POST"])
@login_required
def upload_media():
    if "media" not in request.files:
        flash("No file part", "error")
        return redirect(request.referrer)

    file = request.files["media"]

    if file.filename == "":
        flash("No selected file", "error")
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Optional: Save path to DB if you're attaching it to a message
        flash("File uploaded successfully!", "success")
        return jsonify({
            "success": True,
            "url": url_for("static", filename=f"uploads/{filename}")
        })

    flash("File type not allowed.", "error")
    return jsonify({"success": False})
