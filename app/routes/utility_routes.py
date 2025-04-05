from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash
from flask_mail import Message
from app.database.db import get_db_connection
from app.routes.main_routes import rooms
from app.extensions import mail
from app.config import Config

utility_routes = Blueprint("utility_routes", __name__)

@utility_routes.route("/faq")
def faq():
    return render_template("faq.html")

@utility_routes.route("/tos")
def tos():
    return render_template("tos.html")

@utility_routes.route("/contact", methods=["GET", "POST"])
def contact():
    name = ''
    email = ''
    if 'username' in session:
        name = session['username']
        conn = get_db_connection()
        c = conn.cursor()
        user_email = c.execute('SELECT email FROM users WHERE username = ?', (name,)).fetchone()
        conn.close()
        email = user_email[0] if user_email else ''

    if request.method == 'POST':
        contact_name = request.form.get('name')
        contact_email = request.form.get('email')
        message = request.form.get('message')

        if not contact_name or not contact_email or not message:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('utility_routes.contact'))

        msg = Message(
            subject=f"New Contact Form Submission from {contact_name}",
            sender=Config['MAIL_USERNAME'],
            recipients=['learnwithmegh@gmail.com', 'aadi.pani@gmail.com', 'ayushvinayemail@gmail.com'],
            body=f"Name: {contact_name}\nEmail: {contact_email}\n\nMessage:\n{message}"
        )

        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending the email: {str(e)}', 'error')

        return redirect(url_for('utility_routes.contact'))

    return render_template('contact.html', name=name, email=email)

@utility_routes.route("/get_users/<room>")
def get_users(room):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT user FROM messages WHERE room_number=?", (room,))
    users = cur.fetchall()
    conn.close()

    user_list = [user[0] for user in users if user[0]] 
    return jsonify(users=user_list, count=len(user_list))

@utility_routes.route("/get_messages/<room>")
def get_messages(room):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user, message FROM messages WHERE room_number=?", (room,))
    messages = cur.fetchall()
    conn.close()

    message_list = [{"user": msg[0], "message": msg[1]} for msg in messages]
    return jsonify(messages=message_list)


@utility_routes.route('/active_users', methods=['GET'])
def active_users():
    total_users = sum(room["members"] for room in rooms.values())
    return jsonify(active_users=total_users)

@utility_routes.route('/active_rooms', methods=['GET'])
def active_rooms():
    active_rooms_list = list(rooms.keys())
    return jsonify(active_rooms=active_rooms_list, count=len(active_rooms_list))

@utility_routes.route("/privacy_policy")
def privacy_policy():
    return render_template("policy.html")