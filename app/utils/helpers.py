import random
from string import ascii_uppercase
import sqlite3

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

def caesar_encrypt(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord("a") if char.islower() else ord("A")
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def caesar_decrypt(encrypted_text):
    return caesar_encrypt(encrypted_text, -3)
