import logging
import os
import secrets

from app import app
from database.db import db
from models.models import User
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _seed_admin_password():
    return os.environ.get("ADMIN_PASSWORD", "").strip() or secrets.token_urlsafe(24)


with app.app_context():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@designmatch.com").strip().lower()
    admin_name = os.environ.get("ADMIN_NAME", "Admin Super").strip() or "Admin Super"
    existing = User.query.filter_by(email=admin_email).first()

    if not existing:
        admin = User(
            name=admin_name,
            email=admin_email,
            avatar_url=f"https://api.dicebear.com/9.x/adventurer/svg?seed={admin_name}",
            password_hash=generate_password_hash(_seed_admin_password()),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created for email=%s", admin_email)
    else:
        logger.info("Admin already exists for email=%s", admin_email)

logger.info("Seed complete")
