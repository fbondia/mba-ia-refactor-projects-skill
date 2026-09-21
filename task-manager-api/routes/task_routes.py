from flask import Blueprint, jsonify, request

from controllers.task_controller import TaskController
from middlewares.auth import login_required


task_bp = Blueprint("tasks", __name__)
controller = TaskController()


def respond(result):
    payload, status = result
    return jsonify(payload), status


@task_bp.get("/tasks")
@login_required
def get_tasks(): return respond(controller.list_all())


@task_bp.get("/tasks/search")
@login_required
def search_tasks(): return respond(controller.search(request.args))


@task_bp.get("/tasks/stats")
@login_required
def task_stats(): return respond(controller.stats())


@task_bp.get("/tasks/<int:task_id>")
@login_required
def get_task(task_id): return respond(controller.get(task_id))


@task_bp.post("/tasks")
@login_required
def create_task(): return respond(controller.create(request.get_json(silent=True)))


@task_bp.put("/tasks/<int:task_id>")
@login_required
def update_task(task_id): return respond(controller.update(task_id, request.get_json(silent=True)))


@task_bp.delete("/tasks/<int:task_id>")
@login_required
def delete_task(task_id): return respond(controller.delete(task_id))
