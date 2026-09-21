import logging

from flask import jsonify
from sqlalchemy.exc import IntegrityError

from database import db
from exceptions import ApplicationError


LOGGER = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ApplicationError)
    def application_error(error):
        return jsonify({"error": str(error)}), error.status_code

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        db.session.rollback()
        LOGGER.info("Database constraint rejected request: %s", error)
        return jsonify({"error": "Conflito de dados"}), 409

    @app.errorhandler(Exception)
    def unexpected_error(error):
        db.session.rollback()
        LOGGER.exception("Unhandled request error", exc_info=error)
        return jsonify({"error": "Erro interno"}), 500
