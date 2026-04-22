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

    # ✅ GLOBAL ERROR HANDLER (CORRECT LOCATION)
    @app.errorhandler(Exception)
    def handle_exception(e):
        from werkzeug.exceptions import HTTPException
        import traceback

        if isinstance(e, HTTPException):
            return e

        print("🚨 GLOBAL ERROR:", str(e))
        traceback.print_exc()

        try:
            from models.models import User
            User.query.first()
            print("✅ DB Schema OK")
        except Exception as schema_err:
            print("❌ SCHEMA ISSUE:", str(schema_err))

        return jsonify({
            "success": False,
            "message": "Internal server error - check console logs",
            "debug": str(e),
        }), 500

    return app