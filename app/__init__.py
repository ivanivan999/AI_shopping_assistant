from flask import Flask
from config import Config
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    from app.routes import chat
    app.register_blueprint(chat.bp)
    
    return app