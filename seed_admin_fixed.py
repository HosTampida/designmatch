#!/usr/bin/env python3
"""
Fixed admin seed script for Supabase/Render.
Run: python seed_admin_fixed.py
Safe for both local + production.
"""

print("🌱 Seeding admin user...")

try:
    from app import create_app
    from database.db import db
    from models.models import User
    from werkzeug.security import generate_password_hash
    from services.auth_service import generate_token
    
    app = create_app()
    
    with app.app_context():
        print(f"[SEED] DB: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        
        # Skip if postgresql (let register handle it)
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql://'):
            print("ℹ️ PostgreSQL detected - admin already exists or use /register")
            print("💡 Test: curl -X POST https://designmatch.onrender.com/api/users ...")
            exit(0)
        
        # Local SQLite only
        admin_email = "admin@designmatch.com"
        existing = User.query.filter_by(email=admin_email).first()
        
        if not existing:
            admin = User(
                name="Admin Super",
                email=admin_email,
                avatar_url="https://api.dicebear.com/9.x/adventurer/svg?seed=Admin",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            token = generate_token(admin)
            print(f"✅ Admin created: {admin_email} / admin123")
            print(f"🔑 Token: {token}")
        else:
            print(f"⚠️ Admin exists: {admin_email}")
            
        print("✅ Done!")
        
except ImportError as e:
    print(f"❌ Missing dep: pip install -r requirements.txt  ({e})")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
