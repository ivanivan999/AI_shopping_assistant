# config.py

import os
from datetime import timedelta
from typing import Optional
import uuid
from dataclasses import dataclass

@dataclass
class ChatConfig:
    user_id: str
    thread_id: str
    
    @classmethod
    def from_request(cls, user_id: Optional[str] = None, thread_id: Optional[str] = None) -> dict:
        """Create standardized config dictionary from request data"""
        return {
            "configurable": {
                "user_id": user_id or "USER001",
                "thread_id": thread_id or str(uuid.uuid4())
            }
        }

class Config:
    """Base configuration"""
    # Basic Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-123')
    FLASK_APP = 'run.py'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/shopping.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    BASE_URL = "https://chatapi.littlewheat.com/v1/"
    MODEL_NAME = "gpt-3.5-turbo-0125"
    
    # Chat Settings
    MAX_TOKENS = 1024
    TEMPERATURE = 0.7
    MAX_RETRIES = 2
    REQUEST_TIMEOUT = 30
    
    # Session Configuration 
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_TYPE = 'filesystem'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}