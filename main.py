from app import create_app, socketio, start_background_threads

app = create_app()
start_background_threads()

if __name__ == "__main__":
    socketio.run(app, debug=True)
