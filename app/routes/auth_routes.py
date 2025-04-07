from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db import get_db_connection
from datetime import datetime
auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("auth_routes.signup"))
        if not username or not email or not password:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('auth_routes.signup'))

        conn = get_db_connection()
        cur = conn.cursor()
        user_exists = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user_exists:
            flash("Username already exists", "error")
            conn.close()
            return redirect(url_for("auth_routes.signup"))

        hashed_password = generate_password_hash(password)
        cur.execute('INSERT INTO users (username, email, password, member_since) VALUES (?, ?, ?, ?)', (username, email, hashed_password, datetime.now()))
        conn.commit()
        conn.close()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth_routes.login"))

    return render_template("signup.html")

@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('auth_routes.login'))

        conn = get_db_connection()
        cur = conn.cursor()
        user = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid credentials", "error")
            return redirect(url_for("auth_routes.login"))

        session["username"] = user["username"]
        flash("Logged in successfully", "success")
        return redirect(url_for("main_routes.home"))

    return render_template("login.html")

@auth_routes.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("main_routes.home"))

@auth_routes.route("/user_profile")
def user_profile():
    if "username" not in session:
        flash("Login required", "error")
        return redirect(url_for("auth_routes.login"))
    
    username = session['username']
    conn = get_db_connection()
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    member_since = datetime.strptime(user[4], '%Y-%m-%d %H:%M:%S.%f')
    return render_template('user_profile.html', user=username, email=user['email'], member_since=member_since)

@auth_routes.route("/delete_account", methods=["POST"])
def delete_account():
    if "username" not in session:
        flash("Login required", "error")
        return redirect(url_for("auth_routes.login"))

    username = session["username"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = ?", (username,))
    cur.execute('DELETE FROM messages WHERE user = ?', (username,))
    conn.commit()
    conn.close()

    session.clear()
    flash("Account deleted", "success")
    return redirect(url_for("main_routes.home"))

@auth_routes.route('/modify_account', methods=['GET', 'POST'])
def modify_account():
    if 'username' not in session:
        flash('You need to be logged in to access this page.', 'error')
        return redirect(url_for('auth_routes.login'))

    username = session['username']
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == "POST":
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        current_username, current_email = user['username'], user['email']

        if not user:
            conn.close()
            flash('User not found.', 'error')
            return redirect(url_for('auth_routes.login'))

        if new_username and new_username != current_username:
            username_taken = c.execute('SELECT * FROM users WHERE username = ?', (new_username,)).fetchone()
            if username_taken:
                flash('Username already taken.', 'error')
                return redirect(url_for('auth_routes.modify_account'))
            else:
                c.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, username))
                session['username'] = new_username
                flash('Username updated successfully!', 'success')
                username = new_username
        elif new_username == current_username:
            flash('New username must be different from current username.', 'info')
            return redirect(url_for('auth_routes.modify_account'))

        if new_email and new_email != current_email:
            c.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, username))
            flash('Email updated successfully!', 'success')
        elif new_email == current_email:
            flash('New email must be different from current email.', 'info')
            return redirect(url_for('auth_routes.modify_account'))

        if old_password and new_password and confirm_password:
            if check_password_hash(user['password'], old_password):
                if check_password_hash(user['password'], new_password):
                    flash('New password must be different from old password.', 'error')
                    return redirect(url_for('auth_routes.modify_account'))
                elif new_password != confirm_password:
                    flash('New passwords do not match.', 'error')
                    return redirect(url_for('auth_routes.modify_account'))
                else:
                    hashed = generate_password_hash(new_password)
                    c.execute('UPDATE users SET password = ? WHERE username = ?', (hashed, username))
                    flash('Password updated successfully!', 'success')
            else:
                flash('Old password is incorrect.', 'error')
                return redirect(url_for('auth_routes.modify_account'))

        conn.commit()
        conn.close()

        flash(f'Account modified successfully! Check <a href="{url_for("auth_routes.user_profile")}" class="underline text-purple-400 hover:text-purple-600">dashboard</a> to know more.', 'success')
        return redirect(url_for("main_routes.home"))

    conn.close()
    return render_template("modify_account.html", username=username)
