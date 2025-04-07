from flask import Flask
from dotenv import load_dotenv
import threading
from .config import DevConfig
from .database.db import create_tables
from .extensions import mail, socketio
from .state import cleanup_inactive_rooms
from .sockets.handlers import register_socketio_events
from .routes.main_routes import main_routes as main_bp
from .routes.auth_routes import auth_routes as auth_bp
from .routes.utility_routes import utility_routes as util_bp
from .routes.message_routes import message_routes as message_bp


def create_app():
    # Load environment variables
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # Initialize Flask extensions
    mail.init_app(app)
    socketio.init_app(app)

    # Create DB tables
    create_tables()

    # Register blueprints


    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(util_bp)
    register_socketio_events(socketio)
    app.register_blueprint(message_bp)

    return app

def start_background_threads():
    stop_event = threading.Event()
    cleanup_thread = threading.Thread(
        target=cleanup_inactive_rooms, 
        args=(stop_event,),
        daemon=True
    )
    cleanup_thread.start()
