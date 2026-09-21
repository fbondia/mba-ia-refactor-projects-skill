"""Populate the configured database with development data."""

from datetime import datetime, timedelta, timezone
import os

from application import create_app
from database import db
from models.category import Category
from models.task import Task
from models.user import User


def seed_data():
    passwords = (
        os.environ.get("SEED_ADMIN_PASSWORD"),
        os.environ.get("SEED_USER_PASSWORD"),
        os.environ.get("SEED_MANAGER_PASSWORD"),
    )
    if not all(passwords):
        raise RuntimeError(
            "SEED_ADMIN_PASSWORD, SEED_USER_PASSWORD and SEED_MANAGER_PASSWORD are required"
        )
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = [
            User(name="João Silva", email="joao@email.com", role="admin"),
            User(name="Maria Santos", email="maria@email.com", role="user"),
            User(name="Pedro Oliveira", email="pedro@email.com", role="manager"),
        ]
        for user, password in zip(users, passwords):
            user.set_password(password)
            db.session.add(user)

        categories = [
            Category(name="Backend", description="Tarefas de backend", color="#3498db"),
            Category(name="Frontend", description="Tarefas de frontend", color="#2ecc71"),
            Category(name="DevOps", description="Tarefas de infraestrutura", color="#e74c3c"),
        ]
        db.session.add_all(categories)
        db.session.flush()
        db.session.add_all([
            Task(
                title="Implementar autenticação", description="Adicionar autenticação assinada",
                status="pending", priority=1, user=users[0], category=categories[0],
                due_date=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            Task(
                title="Criar tela de login", description="Tela responsiva",
                status="in_progress", priority=2, user=users[1], category=categories[1],
                due_date=datetime.now(timezone.utc) + timedelta(days=5),
            ),
        ])
        db.session.commit()
        print(f"Seed concluído: {len(users)} usuários, {len(categories)} categorias")


if __name__ == "__main__":
    seed_data()
