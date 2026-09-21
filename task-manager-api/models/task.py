from datetime import datetime, timezone

from database import db


VALID_STATUSES = {"pending", "in_progress", "done", "cancelled"}
MIN_PRIORITY = 1
MAX_PRIORITY = 5


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="pending", nullable=False)
    priority = db.Column(db.Integer, default=3, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    due_date = db.Column(db.DateTime(timezone=True))
    tags = db.Column(db.String(500))

    user = db.relationship("User", back_populates="tasks")
    category = db.relationship("Category", back_populates="tasks")

    @property
    def overdue(self):
        if not self.due_date or self.status in {"done", "cancelled"}:
            return False
        due = self.due_date
        now = datetime.now(timezone.utc)
        if due.tzinfo is None:
            now = now.replace(tzinfo=None)
        return due < now

    def to_dict(self, include_relationships=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "tags": self.tags.split(",") if self.tags else [],
            "overdue": self.overdue,
        }
        if include_relationships:
            data["user_name"] = self.user.name if self.user else None
            data["category_name"] = self.category.name if self.category else None
        return data
