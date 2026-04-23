import logging
import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_database_uri():
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        if database_url.startswith("postgresql://"):
            database_url = _ensure_sslmode(database_url)
        return database_url

    return "sqlite:///designmatch.db"


def _ensure_sslmode(database_url):
    parts = urlsplit(database_url)
    query_params = dict(parse_qsl(parts.query, keep_blank_values=True))

    if "sslmode" not in query_params:
        query_params["sslmode"] = "require"

    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path,
        urlencode(query_params),
        parts.fragment,
    ))


def get_database_label():
    uri = get_database_uri()
    if uri.startswith("postgresql://"):
        return "postgresql"
    if uri.startswith("sqlite:///"):
        return "sqlite (local)"
    return "configured"


def get_secret_key():
    secret_key = os.environ.get("SECRET_KEY", "").strip()
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is required")
    return secret_key


# 🔧 PRODUCTION DETECTION
IS_RENDER = bool(os.environ.get("RENDER_SERVICE_ID"))
SAFE_STARTUP = os.environ.get("SAFE_STARTUP", "false").lower() == "true"
PROD_MODE = IS_RENDER or os.environ.get("FLASK_ENV") == "production"

logger.info("[CONFIG] Environment: RENDER=%s, SAFE=%s, PROD=%s", IS_RENDER, SAFE_STARTUP, PROD_MODE)
logger.info("[CONFIG] DB: %s", get_database_label())

class Config:
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    JSON_SORT_KEYS = False
    
    # Production: always full init for Postgres
    SAFE_STARTUP = False

