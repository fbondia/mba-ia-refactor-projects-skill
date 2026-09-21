from datetime import datetime, timezone

from flask import Flask
from flask_cors import CORS

from config.settings import load_settings
from database import db, enable_sqlite_foreign_keys
from middlewares.error_handler import register_error_handlers
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(load_settings())
    if test_config:
        app.config.update(test_config)

    CORS(app, origins=app.config["CORS_ORIGINS"])
    db.init_app(app)
    enable_sqlite_foreign_keys()
    register_error_handlers(app)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.get("/health")
    def health():
        return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

    @app.get("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    with app.app_context():
        db.create_all()
    return app
