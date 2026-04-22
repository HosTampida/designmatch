from app import app
from database.db import db, init_database
from models.models import User
from werkzeug.security import generate_password_hash
from services.auth_service import generate_token

from app import app
from database.db import db
from models.models import User
from werkzeug.security import generate_password_hash
from services.auth_service import generate_token

with app.app_context():
    db.create_all()
    
    admin_email = "admin@designmatch.com"
    existing = User.query.filter_by(email=admin_email).first()
    if not existing:
        admin = User(
            name="Admin Super",
            email=admin_email,
            avatar_url="https://api.dicebear.com/9.x/adventurer/svg?seed=Admin Super",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        token = generate_token(admin)
        print(f"✅ Admin created: {admin_email} / admin123")
        print(f"Token: {token}")
    else:
        print(f"⚠️ Admin already exists: {admin_email}")

print("Done!")


