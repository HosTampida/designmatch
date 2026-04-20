import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "designmatch-mvp-demo")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///designmatch.db').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
