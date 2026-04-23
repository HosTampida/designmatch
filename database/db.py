import logging
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()


def init_database(app):
    """Production database initialization without runtime schema creation."""
    logger.info("[DB] Initializing database extension")
    db.init_app(app)

    logger.info("[DB] Running startup database checks")
    try:
        with app.app_context():
            logger.info("[DB] Importing models")
            from models.models import Designer, Match, Project, Skill, Style, User  # noqa: F401

            _ensure_postgres_schema()
            if os.environ.get("ENV") == "development":
                seed_data()
            else:
                logger.info("[SEED] Skipping seed_data outside development")

            logger.info("[DB] Startup database checks complete")
    except Exception:
        logger.exception("[DB] Startup database checks failed")
        raise


def _ensure_postgres_schema():
    """Run production-safe PostgreSQL schema guards without dropping data."""
    if db.engine.url.drivername != "postgresql":
        logger.info("[DB] Skipping PostgreSQL schema guard for driver=%s", db.engine.url.drivername)
        return

    with db.engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT"
        ))
    logger.info("[DB] PostgreSQL schema guard applied")


def seed_data():
    """Insert baseline reference data without touching existing rows."""
    logger.info("[SEED] Starting seed_data()")

    if not _reference_tables_ready():
        logger.info("[SEED] Reference tables not available; skipping seed")
        return

    if (db.engine.url.drivername == 'sqlite' and
        os.environ.get('RENDER_SERVICE_ID') and
        not os.path.exists('instance')):
        logger.info("[SEED] Skipping seed for SQLite on Render")
        return

    from models.models import Skill, Style

    logger.info("[SEED] Ensuring skills")
    _ensure_named_rows(Skill, [
        "UI/UX Design", "Web Design", "Logo Design", "Branding", "Social Media Design",
        "Motion Graphics", "3D Design", "Illustration", "Packaging Design", "Video Editing",
        "Typography", "Product Design", "Advertising Design", "App Design", "Visual Identity",
        "Prototipado", "Animación 2D", "Gráfico Digital", "Fotografía", "3D Modeling"
    ])

    logger.info("[SEED] Ensuring styles")
    _ensure_named_rows(Style, [
        "Minimalista", "Vintage", "Moderno", "Brutalista", "Orgánico", "Neón",
        "Flat Design", "Material", "Glassmorphism", "Retro", "Ciberpunk"
    ])

    db.session.commit()
    logger.info("[SEED] Complete")


def _reference_tables_ready():
    inspector = inspect(db.engine)
    required_tables = ("skills", "styles")
    return all(inspector.has_table(table_name) for table_name in required_tables)


def _ensure_named_rows(model, names):
    """Ensure named rows exist, idempotent."""
    logger.info("[SEED] Checking %s", model.__name__)
    row_map = {row.name: row for row in model.query.order_by(model.id).all()}

    created_count = 0
    for name in names:
        if name not in row_map:
            logger.info("[SEED] Creating %s: %s", model.__name__, name)
            row = model(name=name)
            db.session.add(row)
            db.session.flush()
            row_map[name] = row
            created_count += 1

    logger.info("[SEED] %s: %s new rows", model.__name__, created_count)
    return row_map
