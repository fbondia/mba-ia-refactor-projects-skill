from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from database import db
from exceptions import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User


class ReportService:
    @staticmethod
    def summary():
        status_counts = dict(db.session.execute(
            db.select(Task.status, func.count(Task.id)).group_by(Task.status)
        ).all())
        priority_counts = dict(db.session.execute(
            db.select(Task.priority, func.count(Task.id)).group_by(Task.priority)
        ).all())
        tasks = db.session.execute(db.select(Task)).scalars().all()
        seven_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        productivity = db.session.execute(
            db.select(
                User.id, User.name, func.count(Task.id),
                func.sum(db.case((Task.status == "done", 1), else_=0)),
            ).outerjoin(Task).group_by(User.id)
        ).all()
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overview": {
                "total_tasks": sum(status_counts.values()),
                "total_users": db.session.scalar(db.select(func.count(User.id))),
                "total_categories": db.session.scalar(db.select(func.count(Category.id))),
            },
            "tasks_by_status": {name: status_counts.get(name, 0) for name in ("pending", "in_progress", "done", "cancelled")},
            "tasks_by_priority": {
                "critical": priority_counts.get(1, 0), "high": priority_counts.get(2, 0),
                "medium": priority_counts.get(3, 0), "low": priority_counts.get(4, 0),
                "minimal": priority_counts.get(5, 0),
            },
            "overdue": {
                "count": sum(task.overdue for task in tasks),
                "tasks": [task.to_dict() for task in tasks if task.overdue],
            },
            "recent_activity": {
                "tasks_created_last_7_days": db.session.scalar(
                    db.select(func.count(Task.id)).where(Task.created_at >= seven_days_ago)
                ),
                "tasks_completed_last_7_days": db.session.scalar(
                    db.select(func.count(Task.id)).where(Task.status == "done", Task.updated_at >= seven_days_ago)
                ),
            },
            "user_productivity": [
                {
                    "user_id": user_id, "user_name": name, "total_tasks": total,
                    "completed_tasks": completed or 0,
                    "completion_rate": round((completed or 0) / total * 100, 2) if total else 0,
                }
                for user_id, name, total, completed in productivity
            ],
        }

    @staticmethod
    def user_report(user_id):
        user = db.session.get(User, user_id)
        if not user: raise NotFoundError("Usuário não encontrado")
        tasks = db.session.execute(db.select(Task).where(Task.user_id == user_id)).scalars().all()
        counts = {name: sum(task.status == name for task in tasks) for name in ("done", "pending", "in_progress", "cancelled")}
        total = len(tasks)
        return {
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "statistics": {
                "total_tasks": total, **counts,
                "overdue": sum(task.overdue for task in tasks),
                "high_priority": sum(task.priority <= 2 for task in tasks),
                "completion_rate": round(counts["done"] / total * 100, 2) if total else 0,
            },
        }


class CategoryService:
    @staticmethod
    def list_all():
        rows = db.session.execute(
            db.select(Category, func.count(Task.id)).outerjoin(Task).group_by(Category.id)
        ).all()
        return [{**category.to_dict(), "task_count": count} for category, count in rows]

    @staticmethod
    def create(payload):
        values = CategoryService._validate(payload)
        category = Category(**values)
        db.session.add(category)
        db.session.commit()
        return category.to_dict()

    @staticmethod
    def update(category_id, payload):
        category = db.session.get(Category, category_id)
        if not category: raise NotFoundError("Categoria não encontrada")
        for key, value in CategoryService._validate(payload, partial=True).items():
            setattr(category, key, value)
        db.session.commit()
        return category.to_dict()

    @staticmethod
    def delete(category_id):
        category = db.session.get(Category, category_id)
        if not category: raise NotFoundError("Categoria não encontrada")
        db.session.delete(category)
        db.session.commit()
        return {"message": "Categoria deletada"}

    @staticmethod
    def _validate(payload, partial=False):
        if not isinstance(payload, dict): raise ValidationError("Dados inválidos")
        values = {}
        if not partial or "name" in payload:
            name = str(payload.get("name", "")).strip()
            if not name: raise ValidationError("Nome é obrigatório")
            values["name"] = name
        if "description" in payload: values["description"] = str(payload["description"])
        if "color" in payload:
            color = str(payload["color"])
            if len(color) != 7 or not color.startswith("#"):
                raise ValidationError("Cor inválida")
            values["color"] = color
        return values
