import logging
from flask import Flask, send_from_directory
import os
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)
    
    # Lazy imports
    from routes.auth_routes import auth_bp
    from routes.designer_routes import designer_bp
    from routes.project_routes import project_bp
    from database.db import init_database
    
    # API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(designer_bp)
    app.register_blueprint(project_bp)
    
    # Frontend routes
    @app.route('/imagenes/<path:filename>')
    def serve_images(filename):
        return send_from_directory(os.path.join(app.static_folder, 'img'), filename)

    @app.route('/')
    @app.route('/<path:path>')
    def serve_frontend(path='index.html'):
        if path != 'static/<path:filename>' and not path.startswith('api/'):
            return send_from_directory(app.static_folder, 'index.html')
        return send_from_directory(app.static_folder, path)
    
    @app.errorhandler(Exception)
    def handle_error(e):
        logger.exception("Unhandled application error")
        return {'success': False, 'message': 'server error'}, 500
    
    # Production DB init
    with app.app_context():
        init_database(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

