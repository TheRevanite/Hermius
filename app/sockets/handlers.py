from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask import request, session
import sqlite3
from datetime import datetime
import random
from app.utils.helpers import caesar_encrypt
rooms = {}
room_users = {}

def register_socketio_events(socketio: SocketIO):
    
    @socketio.on("connect")
    def connect(auth):
        room = session.get("room")
        name = session.get("name")
        print(f"User connected: {name} to room {room}")
        if not room or not name:
            return
        
        if room not in rooms:
            leave_room(room)
            return

        join_room(room)
        send({"name": name, "message": "has entered the room!"}, to=room)
        rooms[room]["members"] += 1
        print(f"{name} joined room {room}")

    @socketio.on("disconnect_request")
    def disconnect_request():
        room = session.get("room")
        name = session.get("name")

        leave_room(room)

        if room in rooms:
            rooms[room]["members"] -= 1
            if rooms[room]["members"] <= 0:
                del rooms[room]

        send({"name": name, "message": "has left the room"}, to=room)
        print(f"{name} has left the room {room}")

        emit("force_disconnect")

    @socketio.on("join_room")
    def handle_join(data):
        room = data.get("room")

        # Choose name: prefer logged-in username, else persistent anon name
        if "username" in session:
            username = session["username"]
        elif "name" not in session:
            session["name"] = f"Anonymous {random.randint(1, 1000)}"
            username = session["name"]
        else:
            username = session["name"]

        session["room"] = room

        join_room(room)
        room_users.setdefault(room, set()).add(username)

        emit("server_message", {"msg": f"{username} has joined the room."}, room=room)
        emit("update_user_list", list(room_users[room]), room=room)



    @socketio.on("leave_room")
    def handle_leave(data):
        room = data.get("room")
        username = data.get("username", "Anonymous")

        leave_room(room)

        if room in room_users and username in room_users[room]:
            room_users[room].remove(username)

        emit("server_message", {"msg": f"{username} has left the room."}, room=room)
        emit("update_user_list", list(room_users.get(room, [])), room=room)

    @socketio.on("get_users")
    def handle_get_users(data):
        room = data.get("room")
        if room and room in room_users:
            emit("update_user_list", list(room_users[room]), room=room)

    @socketio.on("typing")
    def handle_typing(data):
        room = data.get("room")
        username = data.get("username")
        emit("user_typing", {"username": username}, room=room, include_self=False)

    @socketio.on("stop_typing")
    def handle_stop_typing(data):
        room = data.get("room")
        username = data.get("username")
        emit("user_stopped_typing", {"username": username}, room=room, include_self=False)

    @socketio.on("send_message")
    def handle_send_message(data):
        room = session.get("room")
        username = session.get("name")

        if not room or not username or not data.get("message"):
            return

        message = data["message"]
        encrypted_message = caesar_encrypt(message)

        print(f"[DEBUG] Saving message in room {room}: {message} (Encrypted: {encrypted_message})")

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("""
                INSERT INTO messages (room_number, user, encrypted_message, datetime)
                VALUES (?, ?, ?, ?)
            """, (room, username, encrypted_message, datetime.now()))
            conn.commit()
            print("[DEBUG] Message inserted successfully.")
        except sqlite3.Error as e:
            print(f"[ERROR] Database Error: {e}")
        finally:
            conn.close()
        formatted_time = datetime.now().strftime("%I:%M %p")
        print(f"[DEBUG] Emitting to room: {room} | User: {username} | Message: {message}")
        emit("receive_message", {
            "username": username,
            "message": message,
            "time": formatted_time
        }, to=room)
        print(f"[DEBUG] Emit complete.")


