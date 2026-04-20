import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from db.database import init_db

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure database exists (auto-seeds if needed)
    from config import Config
    if not os.path.exists(Config.DATABASE_PATH):
        from db.seed import seed_all
        init_db()
        seed_all()

    # Register API blueprints
    from routes.curriculum import curriculum_bp
    from routes.kebiao import kebiao_bp
    from routes.generation import generation_bp
    from routes.providers import providers_bp
    from routes.keywords import keywords_bp

    app.register_blueprint(curriculum_bp, url_prefix='/api')
    app.register_blueprint(kebiao_bp, url_prefix='/api')
    app.register_blueprint(generation_bp, url_prefix='/api')
    app.register_blueprint(providers_bp, url_prefix='/api')
    app.register_blueprint(keywords_bp, url_prefix='/api')

    # Serve frontend
    frontend_dir = os.environ.get('FRONTEND_DIR',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'zhibei_frontend'))

    @app.route('/')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(frontend_dir, path)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
