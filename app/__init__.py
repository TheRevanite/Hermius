from flask import Flask
from dotenv import load_dotenv
import os

from .config import DevConfig
from .database.db import create_tables
from .extensions import mail, socketio

rooms = {}  # Optional global dict for tracking chat rooms, etc.

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
    from .routes.main_routes import main_routes as main_bp
    from .routes.auth_routes import auth_routes as auth_bp
    from .routes.utility_routes import utility_routes as util_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(util_bp)

    # Register Socket.IO events
    from .sockets.handlers import register_socketio_events
    register_socketio_events(socketio)

    return app
