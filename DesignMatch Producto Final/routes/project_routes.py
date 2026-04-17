import json

from flask import Blueprint, jsonify, request

from database.db import db
from models.models import Designer, Match, Project
from services.matching_service import rank_designers


project_bp = Blueprint("projects", __name__, url_prefix="/api")


@project_bp.post("/projects")
def create_project():
    payload = request.get_json(silent=True) or {}

    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()

    if not title:
        return jsonify({"success": False, "message": "El titulo es obligatorio"}), 400

    project = Project(
        title=title,
        description=description,
        budget_min=_to_float(payload.get("budget_min")),
        budget_max=_to_float(payload.get("budget_max")),
        urgency=str(payload.get("urgency", "medium")).strip().lower() or "medium",
        required_skill_ids=json.dumps(_clean_id_list(payload.get("skill_ids", []))),
        preferred_style_ids=json.dumps(_clean_id_list(payload.get("style_ids", []))),
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({"success": True, "message": "Proyecto creado", "data": project.to_dict()}), 201


@project_bp.get("/projects/<int:project_id>")
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify({"success": True, "data": project.to_dict()})


@project_bp.get("/projects/<int:project_id>/matches")
def get_project_matches(project_id):
    project = Project.query.get_or_404(project_id)
    designers = Designer.query.order_by(Designer.rating.desc()).all()

    Match.query.filter_by(project_id=project.id).delete()

    ranked_results = rank_designers(project, designers)
    for result in ranked_results:
        db.session.add(
            Match(
                project_id=project.id,
                designer_id=result["designer_id"],
                score=result["score"],
            )
        )

    db.session.commit()

    return jsonify({"success": True, "data": ranked_results})


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
