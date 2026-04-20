import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "designmatch-prod")

    db_url = os.environ.get("DATABASE_URL")

    if db_url:
        # Fix for postgres:// → postgresql://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
    else:
        print("⚠️ DATABASE_URL not found, falling back to SQLite")
        db_url = "sqlite:///designmatch.db"

    print("🔥 DATABASE IN USE:", db_url)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False