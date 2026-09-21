from flask import Blueprint, jsonify, request

from controllers.report_controller import CategoryController, ReportController
from middlewares.auth import admin_required, login_required


report_bp = Blueprint("reports", __name__)
reports = ReportController()
categories = CategoryController()


def respond(result):
    payload, status = result
    return jsonify(payload), status


@report_bp.get("/reports/summary")
@login_required
def summary_report(): return respond(reports.summary())


@report_bp.get("/reports/user/<int:user_id>")
@login_required
def user_report(user_id): return respond(reports.user(user_id))


@report_bp.get("/categories")
@login_required
def get_categories(): return respond(categories.list_all())


@report_bp.post("/categories")
@admin_required
def create_category(): return respond(categories.create(request.get_json(silent=True)))


@report_bp.put("/categories/<int:category_id>")
@admin_required
def update_category(category_id):
    return respond(categories.update(category_id, request.get_json(silent=True)))


@report_bp.delete("/categories/<int:category_id>")
@admin_required
def delete_category(category_id): return respond(categories.delete(category_id))
