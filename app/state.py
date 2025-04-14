import sqlite3
import threading
import time
from datetime import datetime
from app.extensions import socketio

# Mapping room -> set of users
room_users = {}

# Mapping room -> last activity timestamp (not needed if using DB)
room_activity = {}

# Shared state for room creation (used across app)
rooms = {}

# Lock to protect shared state
state_lock = threading.Lock()

# Time (in seconds) before a room is considered inactive
INACTIVITY_TIMEOUT = 120


def add_user_to_room(room, username):
    with state_lock:
        if room not in room_users:
            room_users[room] = set()
        room_users[room].add(username)
        room_activity[room] = time.time()
        if room not in rooms:
            rooms[room] = {"members": 1}
        else:
            rooms[room]["members"] += 1



def remove_user_from_room(room, username):
    print(f"[DEBUG] remove_user_from_room called for room: {room}, username: {username}")  # Debugging
    with state_lock:
        if room in room_users:
            print(f"[DEBUG] Room {room} exists in room_users")  # Debugging
            room_users[room].discard(username)
            print(f"[DEBUG] User {username} removed from room {room}. Remaining users: {room_users[room]}")  # Debugging
            if not room_users[room]:
                print(f"[DEBUG] Room {room} is now empty. Emitting room_deleted event.")  # Debugging
                socketio.emit("room_deleted", {"room_code": room})
                room_users.pop(room)
                room_activity.pop(room, None)
                rooms.pop(room, None)
            else:
                if room in rooms:
                    rooms[room]["members"] = max(0, rooms[room]["members"] - 1)
                    print(f"[DEBUG] Updated room {room} members count: {rooms[room]['members']}")  # Debugging
        else:
            print(f"[DEBUG] Room {room} not found in room_users")  # Debugging

def update_room_activity(room):
    with state_lock:
        room_activity[room] = time.time()


def total_active_users():
    with state_lock:
        return sum(len(users) for users in room_users.values())


def get_active_users_in_room(room):
    with state_lock:
        return room_users.get(room, set())


def cleanup_inactive_rooms(stop_event):
    while not stop_event.is_set():
        now = datetime.now()
        inactive = []

        with state_lock:
            active_rooms = list(room_users.keys())

        for room in active_rooms:
            try:
                with sqlite3.connect("main.db") as conn:
                    c = conn.cursor()
                    c.execute("SELECT MAX(datetime) FROM messages WHERE room_number = ?", (room,))
                    result = c.fetchone()

                if result and result[0]:
                    last_msg_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f" if '.' in result[0] else "%Y-%m-%d %H:%M:%S")
                    if (now - last_msg_time).total_seconds() > INACTIVITY_TIMEOUT:
                        inactive.append(room)

            except Exception as e:
                print(f"[ERROR] Error checking room activity: {e}")

        with state_lock:
            for room in inactive:
                print(f"Emitting room_deleted event for room: {room}")
                socketio.emit("room_deleted", {"room_code": room})

                rooms.pop(room, None)
                room_users.pop(room, None)
                room_activity.pop(room, None)

        stop_event.wait(30)
