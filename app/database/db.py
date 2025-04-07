import sqlite3

def get_db_connection():
    conn = sqlite3.connect("main.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    c = conn.cursor()

    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        member_since TEXT
    )''')

    # Updated Messages Table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT,
        user TEXT,
        encrypted_message TEXT,
        datetime TEXT,
        edited_at TEXT DEFAULT NULL,
        FOREIGN KEY (user) REFERENCES users (username)
    )''')

    # Rooms Table
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_code TEXT UNIQUE NOT NULL,
        created_at TEXT
    )''')

    # NEW: Reports Table
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER,
        reporter TEXT,
        reason TEXT,
        reported_at TEXT,
        FOREIGN KEY (message_id) REFERENCES messages (id),
        FOREIGN KEY (reporter) REFERENCES users (username)
    )''')

    conn.commit()
    conn.close()
