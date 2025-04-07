from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3
import random
from app.utils.helpers import caesar_decrypt, generate_unique_code
from app.database.db import get_db_connection
from app.state import rooms

main_routes = Blueprint('main_routes', __name__)

@main_routes.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        name = session.get('username') or f'Anonymous {random.randint(1, 1000)}'
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create") == "1"

        if join and not code:
            return render_template("home.html", error="Please enter a room code.", code=code)

        conn = sqlite3.connect('main.db')
        c = conn.cursor()
        if create:
            room = generate_unique_code(4)
            try:
                c.execute("INSERT INTO rooms (room_code, created_at) VALUES (?, ?)", (room, datetime.now()))
                conn.commit()

                rooms[room] = {"members": 0, "messages": []}

            except sqlite3.Error as e:
                print(f"[ERROR] Database Error: {e}")
                conn.close()
                return render_template("home.html", error=f"Database error: {str(e)}", code=code)

        else:
            c.execute("SELECT * FROM rooms WHERE room_code = ?", (code,))
            existing_room = c.fetchone()

            if not existing_room:
                conn.close()
                return render_template("home.html", error="Room does not exist.", code=code)

            room=code
        conn.close()
        session["room"] = room
        session["name"] = name
        return redirect(url_for("main_routes.room", room_code=room))

    return render_template("home.html", username=session.get('username'))

@main_routes.route("/room/<room_code>")
def room(room_code):
    if "name" not in session:
        flash("You must join or create a room first.", "error")
        return redirect(url_for("main_routes.home"))

    session["room"] = room_code
    conn = sqlite3.connect('main.db')
    c = conn.cursor()

    room = c.execute("SELECT * FROM rooms WHERE room_code = ?", (room_code,)).fetchone()

    if not room:
        conn.close()
        flash("Room does not exist.", "error")
        return redirect(url_for("main_routes.home"))
    
    c.execute("SELECT user, encrypted_message, datetime FROM messages WHERE room_number=? ORDER BY datetime", (room_code,))
    encrypted_messages = c.fetchall()
    conn.close()
    
    decrypted_messages = []
    for user, encrypted_message, timestamp in encrypted_messages:
        decrypted_message = caesar_decrypt(encrypted_message)
        decrypted_messages.append({"user": user, "message": decrypted_message, "time": timestamp})

    return render_template("room.html", code=room_code, messages=decrypted_messages)


@main_routes.route("/initial_messages/<room_code>")
def initial_messages(room_code):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Fetch all messages for the room from the database
        c.execute("SELECT user, encrypted_message, datetime FROM messages WHERE room_number=? ORDER BY datetime", (room_code,))
        raw_messages = c.fetchall()
    except sqlite3.Error as e:
        print(f"[ERROR] Database Error: {e}")
        return jsonify({"error": "Failed to load messages"}), 500
    finally:
        conn.close()

    messages = []
    current_user= session.get("name", "Anonymous")
    for user, encrypted_message, timestamp in raw_messages:
        user = user or "Anonymous"
        decrypted_message = caesar_decrypt(encrypted_message)
        display_user = "You" if user == current_user else user
        formatted_time = datetime.now().strftime("%I:%M %p")
        messages.append({"user": display_user, "message": decrypted_message, "time": formatted_time})

    # Return all messages as JSON to ensure they are resent upon reload
    return jsonify({"messages": messages})
