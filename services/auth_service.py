from functools import wraps
import logging

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from models.models import User


TOKEN_MAX_AGE_SECONDS = 3600


def generate_token(user):
    serializer = _get_serializer()
    token = serializer.dumps({
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    })
    try:
        current_app.logger.debug("Generated auth token for user_id=%s", user.id)
    except Exception:
        logging.debug("Generated auth token for user_id=%s", user.id)
    return token


def load_user_from_request(required_role=None):
    token = _extract_bearer_token()
    if not token:
        current_app.logger.debug("No Authorization header present")
        return None, _auth_error("Authorization token required", 401)

    try:
        payload = _get_serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except SignatureExpired:
        current_app.logger.info("Expired token provided")
        return None, _auth_error("Authorization token expired", 401)
    except BadSignature:
        current_app.logger.warning("Invalid token provided")
        return None, _auth_error("Invalid authorization token", 401)
    except Exception:
        current_app.logger.exception("Unexpected token validation error")
        return None, _auth_error("Invalid authorization token", 401)

    user_id = payload.get("user_id")
    if not user_id:
        return None, _auth_error("Invalid authorization token", 401)

    user = db_safe_get_user(user_id)
    if not user:
        return None, _auth_error("User not found", 401)

    if required_role and user.role != required_role:
        return None, _auth_error(f"{required_role} access required", 403)

    g.current_user = user
    return user, None


def require_auth(required_role=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            _user, error_response = load_user_from_request(required_role=required_role)
            if error_response is not None:
                return error_response
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def db_safe_get_user(user_id):
    try:
        return User.query.get(user_id)
    except Exception:
        current_app.logger.exception("Failed to load user from token")
        return None


def _extract_bearer_token():
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.replace("Bearer ", "", 1).strip() or None


def _get_serializer():
    secret_key = current_app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret_key, salt="designmatch-auth")


def _auth_error(message, status_code):
    return jsonify({"success": False, "message": message}), status_code
