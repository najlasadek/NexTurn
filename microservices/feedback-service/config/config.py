import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "feedback-secret-key")
    SQLALCHEMY_DATABASE_URI = "sqlite:///db/feedback.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
