from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash


db = SQLAlchemy()


def init_database(app):
    db.init_app(app)

    with app.app_context():
        from models.models import Designer  # noqa: F401

        db.create_all()
        seed_data()


def seed_data():
    # Demo seed data disabled for production use
    # Users can now register real profiles via /api/users
    pass


def _ensure_named_rows(model, names):
    row_map = {row.name: row for row in model.query.order_by(model.id).all()}

    for name in names:
        if name not in row_map:
            row = model(name=name)
            db.session.add(row)
            db.session.flush()
            row_map[name] = row

    return row_map
