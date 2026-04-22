from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_database(app):
    db.init_app(app)

    with app.app_context():
        from models.models import Designer, Skill, Style  # noqa: F401

        db.create_all()
        seed_data()


def seed_data():
    """Insert baseline reference data without touching existing rows."""
    from models.models import Skill, Style

    skill_map = _ensure_named_rows(Skill, [
        "UI/UX Design", "Web Design", "Logo Design", "Branding", "Social Media Design",
        "Motion Graphics", "3D Design", "Illustration", "Packaging Design", "Video Editing",
        "Typography", "Product Design", "Advertising Design", "App Design", "Visual Identity",
        "Prototipado", "Animación 2D", "Gráfico Digital", "Fotografía", "3D Modeling"
    ])

    style_map = _ensure_named_rows(Style, [
        "Minimalista", "Vintage", "Moderno", "Brutalista", "Orgánico", "Neón",
        "Flat Design", "Material", "Glassmorphism", "Retro", "Ciberpunk"
    ])

    db.session.commit()


def _ensure_named_rows(model, names):
    row_map = {row.name: row for row in model.query.order_by(model.id).all()}

    for name in names:
        if name not in row_map:
            row = model(name=name)
            db.session.add(row)
            db.session.flush()
            row_map[name] = row

    return row_map
