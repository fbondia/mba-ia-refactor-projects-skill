import logging
import sqlite3

from flask import jsonify

from src.exceptions import ApplicationError


LOGGER = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ApplicationError)
    def handle_application_error(error):
        return jsonify({"erro": str(error), "sucesso": False}), error.status_code

    @app.errorhandler(sqlite3.IntegrityError)
    def handle_integrity_error(error):
        LOGGER.info("Database constraint rejected request: %s", error)
        return jsonify({"erro": "Conflito de dados", "sucesso": False}), 409

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        LOGGER.exception("Unhandled request error", exc_info=error)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
