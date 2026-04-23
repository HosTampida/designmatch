from flask import Flask, jsonify
import os
from config import Config

# Import AFTER app creation to avoid global init
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Blueprints
    from routes.auth_routes import auth_bp
    from routes.designer_routes import designer_bp
    from routes.project_routes import project_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(designer_bp)
    app.register_blueprint(project_bp)
    
    # DB lazy init
    from database.db import init_database
    with app.app_context():
        safe_mode = app.config.get('SAFE_STARTUP', False)
        init_database(app, safe_mode=safe_mode)
    
    @app.route('/')
    def health():
        return jsonify({'status': 'healthy', 'safe_mode': app.config.get('SAFE_STARTUP', False)})
    
    @app.errorhandler(Exception)
    def handle_error(e):
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'error'}), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Gunicorn compatible: app instance exported

