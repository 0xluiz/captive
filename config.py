import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '1D5gKV8MfmyLMp7WG4zCy'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///captive_portal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configurations
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'suporte@rbtecnologia.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'nneksvqpntzwlmnd'
    MAIL_DEFAULT_SENDER = ('Captive Portal', 'noreply@rbtecnologia.com')
