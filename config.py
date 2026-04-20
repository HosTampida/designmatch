import os


def get_database_uri():
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        return database_url

    return "sqlite:///designmatch.db"


def get_database_label():
    uri = get_database_uri()
    if uri.startswith("postgresql://"):
        return "postgresql"
    if uri.startswith("sqlite:///"):
        return uri
    return "configured"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "designmatch-prod")
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }
    JSON_SORT_KEYS = False
