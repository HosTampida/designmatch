from flask import Flask, jsonify
import os
from urllib.parse import urlsplit, urlunsplit
from werkzeug.exceptions import HTTPException

from config import Config
from database.db import init_database
from routes.auth_routes import auth_bp
from routes.designer_routes import designer_bp
from routes.project_routes import project_bp


def _mask_db_uri(uri: str) -> str:
    """Mask credentials in DB URL for safe logging."""
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


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(Config)
    app.config["PROPAGATE_EXCEPTIONS"] = True

    print("DATABASE:", _mask_db_uri(str(app.config.get("SQLALCHEMY_DATABASE_URI", ""))))

    init_database(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(designer_bp)
    app.register_blueprint(project_bp)

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Keep normal HTTP errors (404, 401, etc.) working as-is.
        if isinstance(e, HTTPException):
            return e

        import traceback

        print("GLOBAL ERROR:", str(e))
        print(traceback.format_exc())

        return jsonify(
            {
                "success": False,
                "message": "Internal server error",
                "debug": str(e),
            }
        ), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 👈 CLAVE para Render
    app.run(host="0.0.0.0", port=port, debug=False)
