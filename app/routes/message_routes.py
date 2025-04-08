from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timezone
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
        if 'name' not in session:
            flash("You must be logged in to perform this action.", "error")
            return redirect(url_for("auth_routes.login"))
        return f(*args, **kwargs)
    return decorated_function


# --- Routes ---

@message_routes.route("/initial_messages/<room>", methods=["GET"])
@login_required
def initial_messages(room):
    conn = get_db_connection()
    c = conn.cursor()
    messages = c.execute(
        "SELECT id AS message_id, user, content AS message, edited_at IS NOT NULL AS edited, created_at AS time "
        "FROM messages WHERE room = ? ORDER BY created_at ASC", (room,)
    ).fetchall()
    conn.close()
    return jsonify({"messages": [dict(msg) for msg in messages]})


@message_routes.route("/delete_message/<int:message_id>", methods=["POST"])
@login_required
def delete_message(message_id):
    conn = get_db_connection()
    c = conn.cursor()

    username = session["name"]
    message = c.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()

    if message and message["user"] == username:
        c.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Message deleted successfully."})
    else:
        conn.close()
        return jsonify({"success": False, "error": "You can only delete your own messages."})


@message_routes.route("/edit_message/<int:message_id>", methods=["POST"])
@login_required
def edit_message(message_id):
    data = request.get_json()
    new_content = data.get("message")
    conn = get_db_connection()
    c = conn.cursor()

    username = session["name"]
    message = c.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()

    if message and message["user"] == username:
        c.execute(
            "UPDATE messages SET content = ?, edited_at = ? WHERE id = ?",
            (new_content, datetime.now(timezone.utc), message_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Message edited successfully."})
    else:
        conn.close()
        return jsonify({"success": False, "error": "You can only edit your own messages."})


@message_routes.route("/report_message/<int:message_id>", methods=["POST"])
@login_required
def report_message(message_id):
    data = request.get_json()
    reason = data.get("reason", "No reason provided")
    conn = get_db_connection()
    c = conn.cursor()

    reporter = session["name"]
    c.execute(
        "INSERT INTO reports (message_id, reporter, reason, reported_at) VALUES (?, ?, ?, ?)",
        (message_id, reporter, reason, datetime.now(timezone.utc))
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Message reported successfully."})


@message_routes.route("/upload_media", methods=["POST"])
@login_required
def upload_media():
    if "media" not in request.files:
        return jsonify({"success": False, "error": "No file part"})

    file = request.files["media"]

    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        return jsonify({
            "success": True,
            "url": url_for("static", filename=f"uploads/{filename}")
        })

    return jsonify({"success": False, "error": "File type not allowed."})
