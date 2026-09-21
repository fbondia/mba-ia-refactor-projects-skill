from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database import db
from exceptions import AuthorizationError, NotFoundError, ValidationError
from models.category import Category
from models.task import MAX_PRIORITY, MIN_PRIORITY, VALID_STATUSES, Task
from models.user import User


class TaskService:
    @staticmethod
    def _visible(actor):
        statement = db.select(Task)
        return statement if actor.is_admin() else statement.where(Task.user_id == actor.id)

    @staticmethod
    def _authorize(task, actor):
        if not actor.is_admin() and task.user_id != actor.id:
            raise AuthorizationError("Operação não autorizada")

    @staticmethod
    def list_all(actor):
        tasks = db.session.execute(
            TaskService._visible(actor).options(joinedload(Task.user), joinedload(Task.category))
        ).scalars().all()
        return [task.to_dict(include_relationships=True) for task in tasks]

    @staticmethod
    def get(task_id, actor):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        TaskService._authorize(task, actor)
        return task.to_dict(include_relationships=True)

    def create(self, payload, actor):
        values = self._normalize(payload, partial=False, actor=actor)
        values.setdefault("user_id", actor.id)
        task = Task(**values)
        db.session.add(task)
        db.session.commit()
        return task.to_dict(), 201

    def update(self, task_id, payload, actor):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        TaskService._authorize(task, actor)
        for key, value in self._normalize(payload, partial=True, actor=actor).items():
            setattr(task, key, value)
        db.session.commit()
        return task.to_dict(), 200

    @staticmethod
    def delete(task_id, actor):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        TaskService._authorize(task, actor)
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deletada com sucesso"}

    @staticmethod
    def search(filters, actor):
        statement = TaskService._visible(actor).options(joinedload(Task.user), joinedload(Task.category))
        query = filters.get("q", "").strip()
        if query:
            statement = statement.where(or_(Task.title.contains(query), Task.description.contains(query)))
        if filters.get("status"):
            if filters["status"] not in VALID_STATUSES:
                raise ValidationError("Status inválido")
            statement = statement.where(Task.status == filters["status"])
        for key, column in (("priority", Task.priority), ("user_id", Task.user_id)):
            if filters.get(key):
                try:
                    statement = statement.where(column == int(filters[key]))
                except ValueError as exc:
                    raise ValidationError(f"{key} inválido") from exc
        tasks = db.session.execute(statement).scalars().all()
        return [task.to_dict(include_relationships=True) for task in tasks]

    @staticmethod
    def stats(actor):
        rows = dict(db.session.execute(
            TaskService._visible(actor).with_only_columns(Task.status, func.count(Task.id)).group_by(Task.status)
        ).all())
        tasks = db.session.execute(TaskService._visible(actor)).scalars().all()
        total = sum(rows.values())
        done = rows.get("done", 0)
        return {
            "total": total,
            "pending": rows.get("pending", 0),
            "in_progress": rows.get("in_progress", 0),
            "done": done,
            "cancelled": rows.get("cancelled", 0),
            "overdue": sum(task.overdue for task in tasks),
            "completion_rate": round(done / total * 100, 2) if total else 0,
        }

    @staticmethod
    def _normalize(payload, partial, actor):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
        if not actor.is_admin() and "user_id" in payload and payload["user_id"] != actor.id:
            raise AuthorizationError("Somente administradores podem atribuir tarefas a outros usuários")
        values = {}
        if not partial or "title" in payload:
            title = str(payload.get("title", "")).strip()
            if not 3 <= len(title) <= 200:
                raise ValidationError("Título deve ter entre 3 e 200 caracteres")
            values["title"] = title
        for key in ("description",):
            if key in payload:
                values[key] = payload[key]
        if not partial or "status" in payload:
            status = payload.get("status", "pending")
            if status not in VALID_STATUSES:
                raise ValidationError("Status inválido")
            values["status"] = status
        if not partial or "priority" in payload:
            try:
                priority = int(payload.get("priority", 3))
            except (TypeError, ValueError) as exc:
                raise ValidationError("Prioridade inválida") from exc
            if not MIN_PRIORITY <= priority <= MAX_PRIORITY:
                raise ValidationError("Prioridade deve ser entre 1 e 5")
            values["priority"] = priority
        for key, model in (("user_id", User), ("category_id", Category)):
            if key in payload:
                value = payload[key]
                if value is not None and not db.session.get(model, value):
                    raise NotFoundError("Usuário não encontrado" if key == "user_id" else "Categoria não encontrada")
                values[key] = value
        if "due_date" in payload:
            if payload["due_date"]:
                try:
                    values["due_date"] = datetime.strptime(payload["due_date"], "%Y-%m-%d")
                except (TypeError, ValueError) as exc:
                    raise ValidationError("Formato de data inválido. Use YYYY-MM-DD") from exc
            else:
                values["due_date"] = None
        if "tags" in payload:
            tags = payload["tags"]
            values["tags"] = ",".join(tags) if isinstance(tags, list) else str(tags)
        return values
