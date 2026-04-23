from flask import Flask, send_from_directory
import os
from config import Config

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
    @app.route('/')
    @app.route('/<path:path>')
    def serve_frontend(path='index.html'):
        if path != 'static/<path:filename>' and not path.startswith('api/'):
            return send_from_directory(app.static_folder, 'index.html')
        return send_from_directory(app.static_folder, path)
    
    @app.route('/api/health')
    def health():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        return {
            'status': 'healthy',
            'database': 'postgresql' if 'postgresql://' in db_uri else 'sqlite',
            'tables_ready': True
        }
    
    @app.errorhandler(Exception)
    def handle_error(e):
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': 'server error'}, 500
    
    # Production DB init
    with app.app_context():
        init_database(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

