from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_database(app):
    """Production database initialization - always full setup."""
    print("[DB] Production full init")
    db.init_app(app)
    
    print("[DB] Running full initialization...")
    try:
        with app.app_context():
            print("[DB] 📥 Importing models...")
            from models.models import Designer, Skill, Style, User, Project, Match  # noqa: F401
            
            print("[DB] 🛠️  Creating tables...")
            db.create_all()
            
            print("[DB] 🌱 Seeding reference data...")
            seed_data()
            
            print("[DB] ✅ Full DB setup complete")
            
    except Exception as e:
        print(f"[DB] ❌ Full init failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def seed_data():
    """Insert baseline reference data without touching existing rows."""
    print("[SEED] Starting seed_data()...")
    
    # Skip seeding if SQLite in production context (Render can't write)
    if (db.engine.url.drivername == 'sqlite' and 
        os.environ.get('RENDER_SERVICE_ID') and 
        not os.path.exists('instance')):
        print("[SEED] Skipping - SQLite on Render (no persistent storage)")
        return
    
    from models.models import Skill, Style

    print("[SEED] Ensuring skills...")
    skill_map = _ensure_named_rows(Skill, [
        "UI/UX Design", "Web Design", "Logo Design", "Branding", "Social Media Design",
        "Motion Graphics", "3D Design", "Illustration", "Packaging Design", "Video Editing",
        "Typography", "Product Design", "Advertising Design", "App Design", "Visual Identity",
        "Prototipado", "Animación 2D", "Gráfico Digital", "Fotografía", "3D Modeling"
    ])

    print("[SEED] Ensuring styles...")
    style_map = _ensure_named_rows(Style, [
        "Minimalista", "Vintage", "Moderno", "Brutalista", "Orgánico", "Neón",
        "Flat Design", "Material", "Glassmorphism", "Retro", "Ciberpunk"
    ])

    db.session.commit()
    print("[SEED] ✅ Complete")

def _ensure_named_rows(model, names):
    """Ensure named rows exist, idempotent."""
    print(f"[SEED] Checking {model.__name__}...")
    row_map = {row.name: row for row in model.query.order_by(model.id).all()}

    created_count = 0
    for name in names:
        if name not in row_map:
            print(f"[SEED] Creating {model.__name__}: {name}")
            row = model(name=name)
            db.session.add(row)
            db.session.flush()
            row_map[name] = row
            created_count += 1

    print(f"[SEED] {model.__name__}: {created_count} new rows")
    return row_map

