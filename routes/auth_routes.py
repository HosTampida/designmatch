from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from database.db import db
from models.models import Designer, DesignerSkill, Match, Project, Skill, Style, User
from services.auth_service import generate_token


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.get("/health")
def health_check():
    database_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    return jsonify(
        {
            "success": True,
            "message": "DesignMatch is operational",
            "data": {
                "status": "ok",
                "database": "postgresql" if str(database_uri).startswith("postgresql://") else "sqlite",
            },
        }
    )


@auth_bp.post("/auth/register")
@auth_bp.post("/users")
def create_user():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    role = str(payload.get("role", "client")).strip().lower() or "client"
    password = str(payload.get("password", "")).strip()

    if not name or not email or not password:
        return jsonify({"success": False, "message": "name, email y password son obligatorios"}), 400

    if role not in {"designer", "client"}:
        return jsonify({"success": False, "message": "role must be designer or client"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"success": False, "message": "Email already registered"}), 409

    user = User(
        name=name,
        email=email,
        phone=payload.get("phone"),
        project_description=payload.get("project_description") if role == "client" else None,
        password_hash=generate_password_hash(password),
        role=role,
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
            completed_projects=int(payload.get("completed_projects", 0) or 0),
        )
        db.session.add(designer)
        db.session.flush()

        skill_ids = _clean_id_list(payload.get("skills", []))
        for skill in Skill.query.filter(Skill.id.in_(skill_ids)).all():
            db.session.add(DesignerSkill(designer_id=designer.id, skill_id=skill.id))

    db.session.commit()
    token = generate_token(user)

    return jsonify(
        {
            "success": True,
            "message": "Account created successfully",
            "data": {"user": user.to_dict(), "token": token},
        }
    ), 201


@auth_bp.post("/auth/login")
@auth_bp.post("/login")
def login():
    try:
        payload = request.get_json(silent=True) or {}
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", "")).strip()

        if not email or not password:
            current_app.logger.warning("Login attempt with missing credentials: %s", email)
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            current_app.logger.warning("Login failed - user not found: %s", email)
            return jsonify({"success": False, "message": "Invalid credentials"}), 401

        if not check_password_hash(user.password_hash, password):
            current_app.logger.warning("Login failed - wrong password for user: %s", email)
            return jsonify({"success": False, "message": "Invalid credentials"}), 401

        token = generate_token(user)
        current_app.logger.info("User logged in: %s (id=%s)", email, user.id)

        return jsonify(
            {
                "success": True,
                "message": "Session started",
                "data": {"user": user.to_dict(), "token": token},
            }
        )
    except Exception as exc:
        current_app.logger.error("Unexpected error during login for %s: %s",
                                 payload.get("email") if isinstance(payload, dict) else None,
                                 str(exc))
        return jsonify({"success": False, "message": "Internal server error"}), 500


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
                "applications": Match.query.count(),
            },
        }
    )


@auth_bp.get("/info")
def get_info():
    database_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    return jsonify(
        {
            "success": True,
            "data": {
                "name": "DesignMatch",
                "description": "Connect clients with designers for real projects.",
                "version": "1.0",
                "database": "postgresql" if str(database_uri).startswith("postgresql://") else "sqlite",
                "features": [
                    "Browse designer catalog",
                    "Create projects quickly",
                    "Get match rankings",
                    "Register as designer or client",
                ],
            },
        }
    )

@auth_bp.delete("/users/<int:user_id>")
def delete_user(user_id):
    from services.auth_service import require_auth
    user, error = require_auth("admin")()
    if error:
        return error
    
    target = User.query.get_or_404(user_id)
    db.session.delete(target)
    db.session.commit()
    return jsonify({"success": True, "message": f"User {target.email} deleted"}), 200

def _clean_id_list(raw_values):
    clean_ids = []
    for value in raw_values or []:
        try:
            clean_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    return clean_ids
