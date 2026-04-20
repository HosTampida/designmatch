from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from database.db import db
from models.models import Designer, Match, Project, Skill, Style, User


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.get("/health")
def health_check():
    return jsonify(
        {
            "success": True,
            "message": "DesignMatch is operational",
            "data": {"status": "ok", "database": "sqlite:///designmatch.db"},
        }
    )


@auth_bp.post("/users")
def create_user():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    role = str(payload.get("role", "client")).strip().lower() or "client"

    if not name or not email:
        return jsonify({"success": False, "message": "name y email son obligatorios"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify(
            {
                "success": True,
                "message": "El usuario ya existe",
                "data": {"id": existing.id, "name": existing.name, "email": existing.email, "role": existing.role},
            }
        )

    user = User(
        name=name,
        email=email,
        phone=payload.get("phone"),
        project_description=payload.get("project_description") if role == "client" else None,
        password_hash=generate_password_hash(payload.get("password", "default123")),
        role="designer" if role == "designer" else "client",
    )
    db.session.add(user)
    db.session.flush()

    if role == "designer":
        designer = Designer(
            user_id=user.id,
            phone=payload.get("phone"),
            bio=payload.get("bio", ""),
            portfolio_url=payload.get("portfolio_url", ""),
            price_min=float(payload.get("price_min", 0)),
            price_max=float(payload.get("price_max", 0)),
            rating=float(payload.get("rating", 0)),
        )
        db.session.add(designer)

        # Add skills if provided (now IDs)
        skill_ids = payload.get("skills", [])
        if skill_ids:
            for skill_id in skill_ids:
                skill = Skill.query.get(skill_id)
                if skill:
                    db.session.add(DesignerSkill(designer_id=designer.id, skill_id=skill.id))

    db.session.commit()
    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Account created successfully",
            "data": {"id": user.id, "name": user.name, "email": user.email, "role": user.role},
        }
    ), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()

    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify(
        {
            "success": True,
            "message": "Session started",
            "data": {"id": user.id, "name": user.name, "email": user.email, "role": user.role},
        }
    )


@auth_bp.get("/stats")
def get_stats():
    return jsonify(
        {
            "success": True,
            "data": {
                "designers": Designer.query.count(),
                "skills": Skill.query.count(),
                "styles": Style.query.count(),
                "projects": Project.query.count(),
                "matches": Match.query.count(),
            },
        }
    )


@auth_bp.get("/info")
def get_info():
    return jsonify(
        {
            "success": True,
            "data": {
                "name": "DesignMatch",
                "description": "Connect clients with designers for real projects.",
                "version": "1.0",
                "database": "sqlite:///designmatch.db",
                "features": [
                    "Browse designer catalog",
                    "Create projects quickly",
                    "Get match rankings",
                    "Register as designer or client",
                ],
            },
        }
    )
