import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_default_secret")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_RECIPIENTS=os.getenv("MAIL_RECIPIENTS", "").split(",")

class DevConfig(Config):
    DEBUG = True