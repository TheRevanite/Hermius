from app import create_app, socketio, start_background_threads
from flask import render_template

app = create_app()
start_background_threads()

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    socketio.run(app)