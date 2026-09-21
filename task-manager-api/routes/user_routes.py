from flask import Blueprint, g, jsonify, request

from controllers.user_controller import UserController
from middlewares.auth import admin_required, login_required


user_bp = Blueprint("users", __name__)
controller = UserController()


def respond(result):
    payload, status = result
    return jsonify(payload), status


@user_bp.get("/users")
@admin_required
def get_users(): return respond(controller.list_all())


@user_bp.get("/users/<int:user_id>")
@login_required
def get_user(user_id): return respond(controller.get(user_id, g.current_user))


@user_bp.post("/users")
def create_user(): return respond(controller.create(request.get_json(silent=True)))


@user_bp.put("/users/<int:user_id>")
@login_required
def update_user(user_id):
    return respond(controller.update(user_id, request.get_json(silent=True), g.current_user))


@user_bp.delete("/users/<int:user_id>")
@login_required
def delete_user(user_id): return respond(controller.delete(user_id, g.current_user))


@user_bp.get("/users/<int:user_id>/tasks")
@login_required
def get_user_tasks(user_id):
    payload, status = controller.get(user_id, g.current_user)
    return jsonify(payload["tasks"]), status


@user_bp.post("/login")
def login(): return respond(controller.login(request.get_json(silent=True)))
