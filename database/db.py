from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_database(app):
    db.init_app(app)

    with app.app_context():
        print("🔥 INIT DATABASE START")

        from models.models import Designer, Skill, Style  # noqa

        # Crear tablas
        db.create_all()
        print("✅ Tables created (if not exist)")

        # Seed seguro
        seed_data()

        print("🔥 INIT DATABASE DONE")


def seed_data():
    """Prod-safe auto-seed: Add skills/styles if under minimum."""
    from models.models import Skill, Style

    print("🌱 Seeding skills and styles...")

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
    print(f"✅ Skills: {len(skill_map)} | Styles: {len(style_map)}")


def _ensure_named_rows(model, names):
    row_map = {row.name: row for row in model.query.order_by(model.id).all()}

    for name in names:
        if name not in row_map:
            row = model(name=name)
            db.session.add(row)
            db.session.flush()
            row_map[name] = row

    return row_map