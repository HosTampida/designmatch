from flask import Blueprint, current_app, jsonify, request
from urllib.parse import urlsplit, urlunsplit
from werkzeug.security import generate_password_hash

from database.db import db
from models.models import Designer, DesignerSkill, DesignerStyle, Skill, Style, User


designer_bp = Blueprint("designers", __name__, url_prefix="/api")


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


@designer_bp.get("/designers")
def list_designers():
    try:
        _debug_db("GET /api/designers")
        skill_filter = request.args.get("skill", "").strip()
        style_filter = request.args.get("style", "").strip()
        max_price = _to_float(request.args.get("max_price"), default=None)
        query = Designer.query

        if skill_filter:
            query = query.join(DesignerSkill).join(Skill).filter(
                Skill.name.ilike(f"%{skill_filter}%")
            ).distinct()

        if style_filter:
            query = query.join(DesignerStyle).join(Style).filter(
                Style.name.ilike(f"%{style_filter}%")
            ).distinct()

        if max_price is not None:
            query = query.filter(Designer.price_min <= max_price)

        designers = query.order_by(Designer.rating.desc(), Designer.id.asc()).all()
        payload = []
        for designer in designers:
            try:
                payload.append(designer.to_card_dict())
            except Exception as exc:
                print("ERROR: to_card_dict failed:", str(exc))
                raise

        return jsonify({"success": True, "data": payload})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@designer_bp.get("/designers/<int:designer_id>")
def get_designer(designer_id):
    try:
        _debug_db("GET /api/designers/<id>")
        designer = Designer.query.get_or_404(designer_id)
        return jsonify({"success": True, "data": designer.to_card_dict()})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@designer_bp.get("/skills")
def list_skills():
    try:
        _debug_db("GET /api/skills")
        skills = Skill.query.order_by(Skill.name.asc()).all()
        return jsonify({"success": True, "data": [{"id": skill.id, "name": skill.name} for skill in skills]})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@designer_bp.get("/styles")
def list_styles():
    try:
        _debug_db("GET /api/styles")
        styles = Style.query.order_by(Style.name.asc()).all()
        return jsonify({"success": True, "data": [{"id": style.id, "name": style.name} for style in styles]})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


@designer_bp.post("/designers/import")
def import_designers():
    try:
        _debug_db("POST /api/designers/import")
        payload = request.get_json(silent=True)
        if not isinstance(payload, list):
            return jsonify({"success": False, "message": "Body must be a JSON array"}), 400

        created = []
        updated = []

        for item in payload:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            email = str(item.get("email", "")).strip().lower()

            if not name or not email:
                continue

            user = User.query.filter_by(email=email).first()
            if user and user.designer_profile:
                designer = user.designer_profile
                user.name = name
                designer.bio = str(item.get("bio", "")).strip()
                designer.portfolio_url = str(item.get("portfolio_url", "")).strip()
                designer.price_min = _to_float(item.get("price_min"))
                designer.price_max = _to_float(item.get("price_max"))
                designer.rating = _to_float(item.get("rating"), 4.5)
                updated.append(email)
            else:
                if not user:
                    user = User(
                        name=name,
                        email=email,
                        avatar_url=generate_avatar_url(name),
                        password_hash=generate_password_hash("demo123"),
                        role="designer",
                    )
                    db.session.add(user)
                    db.session.flush()
                else:
                    user.name = name
                    user.role = "designer"

                designer = Designer(
                    user_id=user.id,
                    bio=str(item.get("bio", "")).strip(),
                    portfolio_url=str(item.get("portfolio_url", "")).strip(),
                    price_min=_to_float(item.get("price_min")),
                    price_max=_to_float(item.get("price_max")),
                    rating=_to_float(item.get("rating"), 4.5),
                )
                db.session.add(designer)
                db.session.flush()
                created.append(email)

            _replace_designer_links(designer, item.get("skills", []), item.get("styles", []))

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Designer import completed",
                "data": {
                    "created": len(created),
                    "updated": len(updated),
                    "emails": created + updated,
                },
            }
        )
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "message": "Internal server error", "debug": str(e)}), 500


def _replace_designer_links(designer, skill_ids, style_ids):
    DesignerSkill.query.filter_by(designer_id=designer.id).delete()
    DesignerStyle.query.filter_by(designer_id=designer.id).delete()

    valid_skill_ids = {skill.id for skill in Skill.query.filter(Skill.id.in_(_clean_id_list(skill_ids))).all()}
    valid_style_ids = {style.id for style in Style.query.filter(Style.id.in_(_clean_id_list(style_ids))).all()}

    for skill_id in valid_skill_ids:
        db.session.add(DesignerSkill(designer_id=designer.id, skill_id=skill_id))

    for style_id in valid_style_ids:
        db.session.add(DesignerStyle(designer_id=designer.id, style_id=style_id))


def _clean_id_list(raw_values):
    clean_ids = []
    for value in raw_values or []:
        try:
            clean_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    return clean_ids


def _to_float(value, default=0.0):
    if value in (None, "") and default is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        if default is None:
            return None
        return float(default)
