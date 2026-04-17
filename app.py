from flask import Flask, jsonify
import os

from config import Config
from database.db import init_database
from routes.auth_routes import auth_bp
from routes.designer_routes import designer_bp
from routes.project_routes import project_bp


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(Config)

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

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 👈 CLAVE para Render
    app.run(host="0.0.0.0", port=port, debug=False)