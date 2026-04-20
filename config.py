import os


class Config:
<<<<<<< HEAD
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
=======
    SECRET_KEY = os.environ.get("SECRET_KEY", "designmatch-mvp-demo")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///designmatch.db').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
>>>>>>> 79ff929e95bb420a457977a7a512c18b5b057754
