from flask import Flask
from flask_cors import CORS

from src.config.settings import load_settings
from src.infrastructure.database import init_database
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import api


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(load_settings())
    if test_config:
        app.config.update(test_config)

    CORS(app, origins=app.config["CORS_ORIGINS"])
    init_database(app)
    register_error_handlers(app)
    app.register_blueprint(api)
    return app
