from flask import Blueprint, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename

from datetime import datetime, timezone
from ..database.db import get_db_connection
from functools import wraps


message_routes = Blueprint("message_routes", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'name' not in session:
            flash("You must be logged in to perform this action.", "error")
            return redirect(url_for("auth_routes.login"))
        return f(*args, **kwargs)
    return decorated_function

@message_routes.route("/initial_messages/<room>", methods=["GET"])
@login_required
def initial_messages(room):
    conn = get_db_connection()
    c = conn.cursor()
    messages = c.execute(
        "SELECT id AS message_id, user, content AS message, created_at AS time "
        "FROM messages WHERE room = ? ORDER BY created_at ASC", (room,)
    ).fetchall()
    conn.close()
    return jsonify({"messages": [dict(msg) for msg in messages]})
