from datetime import timedelta

class Config:

    # =========================
    # MySQL Database Connection
    # =========================
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root%40123@localhost/company'

    # Disable SQLAlchemy warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # =========================
    # Flask Secret Key
    # =========================
    SECRET_KEY = 'employee123'


    # =========================
    # Session Configuration
    # =========================

    # User session will expire after 30 minutes of inactivity
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)


    # =========================
    # JWT Configuration
    # =========================
    JWT_SECRET_KEY = 'jwt-secret-key-123'


    # Access Token Expiry Time
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


    # Refresh Token Expiry Time
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


    # Optional JWT Settings
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'