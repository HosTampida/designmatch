from flask import Flask, jsonify
from config import Config
from database.db import init_database
from routes.auth_routes import auth_bp
from routes.designer_routes import designer_bp
from routes.project_routes import project_bp

from werkzeug.exceptions import HTTPException
import traceback
import os

def _mask_db_uri(uri):
    """Mask sensitive parts of DB URI for logs."""
    if not uri:
        return "<none>"
    try:
        from urllib.parse import urlsplit
        parts = urlsplit(uri)
        if "@" not in parts.netloc:
            return uri
        userinfo, host = parts.netloc.split("@", 1)
        username = userinfo.split(":")[0] if ":" in userinfo else userinfo
        masked = f"{username}:***@{host}"
        return parts._replace(netloc=masked).geturl()
    except:
        return "<error>"

def create_app():
    print("[STARTUP] 🚀 1/6 Creating Flask app...")
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    
    print("[STARTUP] 📋 2/6 Loading config...")
    app.config.from_object(Config)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    
    print(f"[STARTUP] 🗄️  3/6 DB URI: {_mask_db_uri(str(app.config.get('SQLALCHEMY_DATABASE_URI', '')))}")
    
    # Auto-detect safe mode for production/Render
    safe_mode = not app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql://")
    print(f"[STARTUP] 🛡️  4/6 DB Init {'(SAFE MODE)' if safe_mode else '(FULL)'}...")
    
    try:
        init_database(app, safe_mode=safe_mode)
        print("[STARTUP] ✅ 4/6 DB initialization SUCCESS")
    except Exception as db_err:
        print(f"[STARTUP] ❌ 4/6 DB initialization FAILED: {str(db_err)}")
        print("[STARTUP] ℹ️  Continuing in degraded mode (no DB)...")
        import traceback
        traceback.print_exc()
    
    print("[STARTUP] 🔌 5/6 Registering blueprints...")
    app.register_blueprint(auth_bp)
    app.register_blueprint(designer_bp)
    app.register_blueprint(project_bp)
    
    print("[STARTUP] 🌐 6/6 Adding routes...")
    
    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    # GLOBAL ERROR HANDLER - catches everything
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e

        print("🚨 UNHANDLED ERROR:", str(e))
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Internal server error - check logs",
            "debug": str(e),
        }), 500

    print("🎉 [STARTUP] Flask app READY!")
    return app

if __name__ == "__main__":
    print("[MAIN] Starting Flask dev server...")
    app = create_app()
    print("[MAIN] Dev server listening on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

