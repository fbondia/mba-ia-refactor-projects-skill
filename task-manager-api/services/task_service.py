from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database import db
from exceptions import NotFoundError, ValidationError
from models.category import Category
from models.task import MAX_PRIORITY, MIN_PRIORITY, VALID_STATUSES, Task
from models.user import User


class TaskService:
    @staticmethod
    def list_all():
        tasks = db.session.execute(
            db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
        ).scalars().all()
        return [task.to_dict(include_relationships=True) for task in tasks]

    @staticmethod
    def get(task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        return task.to_dict(include_relationships=True)

    def create(self, payload):
        values = self._normalize(payload, partial=False)
        task = Task(**values)
        db.session.add(task)
        db.session.commit()
        return task.to_dict(), 201

    def update(self, task_id, payload):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        for key, value in self._normalize(payload, partial=True).items():
            setattr(task, key, value)
        db.session.commit()
        return task.to_dict(), 200

    @staticmethod
    def delete(task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deletada com sucesso"}

    @staticmethod
    def search(filters):
        statement = db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
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
    def stats():
        rows = dict(db.session.execute(
            db.select(Task.status, func.count(Task.id)).group_by(Task.status)
        ).all())
        tasks = db.session.execute(db.select(Task)).scalars().all()
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
    def _normalize(payload, partial):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
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
