import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "designmatch-mvp-demo")
    SQLALCHEMY_DATABASE_URI = "sqlite:///designmatch.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
