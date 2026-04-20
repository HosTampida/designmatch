from functools import wraps

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, URLSafeSerializer

from models.models import User


def generate_token(user):
    serializer = _get_serializer()
    return serializer.dumps({
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    })


def load_user_from_request(required_role=None):
    token = _extract_bearer_token()
    if not token:
        return None, _auth_error("Authorization token required", 401)

    try:
        payload = _get_serializer().loads(token)
    except BadSignature:
        return None, _auth_error("Invalid token", 401)

    user = User.query.get(payload.get("user_id"))
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


def _extract_bearer_token():
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.replace("Bearer ", "", 1).strip() or None


def _get_serializer():
    secret_key = current_app.config.get("SECRET_KEY", "designmatch-prod")
    return URLSafeSerializer(secret_key, salt="designmatch-auth")


def _auth_error(message, status_code):
    return jsonify({"success": False, "message": message}), status_code
