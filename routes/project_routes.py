import json

from flask import Blueprint, current_app, jsonify, request
from urllib.parse import urlsplit, urlunsplit

from database.db import db
from models.models import Designer, Match, Project, User
from services.auth_service import require_auth
from services.matching_service import rank_designers


project_bp = Blueprint("projects", __name__, url_prefix="/api")


def _mask_db_uri(uri: str) -> str:
    try:
        parts = urlsplit(uri)
        if "@" not in parts.netloc or ":" not in parts.netloc.split("@", 1)[0]:
            return uri
        userinfo, hostinfo = parts.netloc.split("@", 1)
        username = userinfo.split(":", 1)[0]
        netloc = f"{username}:***@{hostinfo}"
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    except Exception:
        return "<unavailable>"


def _debug_db(where: str):
    uri = str(current_app.config.get("SQLALCHEMY_DATABASE_URI", ""))
    print(f"[DB DEBUG] {where} uri={_mask_db_uri(uri)}")
    try:
        probe = User.query.first()
        print("[DB DEBUG] User.query.first() OK:", probe)
    except Exception as exc:
        print("[DB DEBUG] User.query.first() FAILED:", str(exc))
        raise


@project_bp.post("/projects")
@require_auth(required_role="client")
def create_project():
    try:
        _debug_db("POST /api/projects")
        payload = request.get_json(silent=True) or {}
        from flask import g

        title = str(payload.get("title", "")).strip()
        description = str(payload.get("description", "")).strip()

        if not title:
            return jsonify({"success": False, "message": "El titulo es obligatorio"}), 400

        skill_ids = _clean_id_list(payload.get("skill_ids", []))
        style_ids = _clean_id_list(payload.get("style_ids", []))
        budget = _to_float(payload.get("budget"))

        project = Project(
            client_id=g.current_user.id,
            title=title,
            description=description,
            budget=budget if budget > 0 else _to_float(payload.get("budget_max")),
            budget_min=_to_float(payload.get("budget_min")),
            budget_max=_to_float(payload.get("budget_max")) or budget,
            urgency=str(payload.get("urgency", "medium")).strip().lower() or "medium",
            required_skill_ids=json.dumps(skill_ids),
            preferred_style_ids=json.dumps(style_ids),
            skills_used=json.dumps(payload.get("skills_used", skill_ids)),
        )

        db.session.add(project)
        db.session.commit()

        return jsonify({"success": True, "message": "Proyecto creado", "data": project.to_dict()}), 201
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@project_bp.get("/projects")
def list_projects():
    try:
        _debug_db("GET /api/projects")
        projects = Project.query.order_by(Project.created_at.desc(), Project.id.desc()).all()
        for project in projects:
            project.views_count = int(project.views_count or 0) + 1
        db.session.commit()
        return jsonify({"success": True, "data": [project.to_dict() for project in projects]})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@project_bp.get("/projects/<int:project_id>")
def get_project(project_id):
    try:
        _debug_db("GET /api/projects/<id>")
        project = Project.query.get_or_404(project_id)
        project.views_count = int(project.views_count or 0) + 1
        db.session.commit()
        return jsonify({"success": True, "data": project.to_dict()})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@project_bp.post("/projects/<int:project_id>/apply")
@require_auth(required_role="designer")
def apply_to_project(project_id):
    try:
        _debug_db("POST /api/projects/<id>/apply")
        from flask import g

        project = Project.query.get_or_404(project_id)
        designer = Designer.query.filter_by(user_id=g.current_user.id).first()
        if not designer:
            return jsonify({"success": False, "message": "Designer profile not found"}), 404

        existing = Match.query.filter_by(project_id=project.id, designer_id=designer.id).first()
        if existing:
            return jsonify({"success": False, "message": "Already applied to this project"}), 409

        match = Match(project_id=project.id, designer_id=designer.id, status="pending")
        db.session.add(match)
        project.applications_count = int(project.applications_count or 0) + 1
        db.session.commit()

        return jsonify({"success": True, "message": "Application submitted", "data": match.to_dict()}), 201
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@project_bp.post("/projects/<int:project_id>/select/<int:designer_id>")
@require_auth(required_role="client")
def select_designer(project_id, designer_id):
    try:
        _debug_db("POST /api/projects/<id>/select/<id>")
        from flask import g

        project = Project.query.get_or_404(project_id)
        if project.client_id != g.current_user.id:
            return jsonify({"success": False, "message": "You can only manage your own projects"}), 403

        selected_match = Match.query.filter_by(project_id=project.id, designer_id=designer_id).first()
        if not selected_match:
            return jsonify({"success": False, "message": "Application not found"}), 404

        already_accepted = selected_match.status == "accepted"

        for match in Match.query.filter_by(project_id=project.id).all():
            if match.designer_id == designer_id:
                match.status = "accepted"
            else:
                match.status = "rejected"

        if not already_accepted and selected_match.designer:
            selected_match.designer.completed_projects = int(selected_match.designer.completed_projects or 0) + 1

        db.session.commit()
        return jsonify({"success": True, "message": "Designer selected", "data": selected_match.to_dict()})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@project_bp.get("/projects/<int:project_id>/matches")
def get_project_matches(project_id):
    try:
        _debug_db("GET /api/projects/<id>/matches")
        project = Project.query.get_or_404(project_id)
        designers = Designer.query.order_by(Designer.rating.desc()).all()
        existing_matches = {
            match.designer_id: match
            for match in Match.query.filter_by(project_id=project.id).all()
        }

        ranked_results = rank_designers(project, designers)
        for result in ranked_results:
            existing_match = existing_matches.get(result["designer_id"])
            result["status"] = existing_match.status if existing_match else "not_applied"

        return jsonify({"success": True, "data": ranked_results})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


def _clean_id_list(raw_values):
    clean_ids = []
    for value in raw_values or []:
        try:
            clean_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    return clean_ids


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
