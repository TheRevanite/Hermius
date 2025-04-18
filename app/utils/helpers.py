import random
from string import ascii_uppercase
import sqlite3
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

key=generate_key()
cipher_suite = Fernet(key)

def encrypt_message(message):
    if isinstance(message, str):
        message = message.encode()
    encrypted_message = cipher_suite.encrypt(message)
    return encrypted_message

def decrypt_message(encrypted_message):
    if isinstance(encrypted_message, str):
        encrypted_message = encrypted_message.encode()
    decrypted_message = cipher_suite.decrypt(encrypted_message)
    return decrypted_message.decode()


def generate_unique_code(length):
    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        existing_room = c.execute("SELECT * FROM rooms WHERE room_code = ?", (code,)).fetchone()
        if not existing_room:
            break
    conn.close()
    return code