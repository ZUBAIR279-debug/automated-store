import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # ---- Database: absolute path based on this file's location ----
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(BASE_DIR, 'database')
    
    # Create the 'database' folder if it doesn't exist
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    
    DB_PATH = os.path.join(DB_DIR, 'store.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Third‑party credentials (placeholders)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN', '')
    GEMINI_API_KEY     = os.environ.get('GEMINI_API_KEY', '')
    TCS_API_KEY        = os.environ.get('TCS_API_KEY', '')
    OWNER_WHATSAPP_NUMBER = os.environ.get('OWNER_WHATSAPP_NUMBER', '+923001234567')
    
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}