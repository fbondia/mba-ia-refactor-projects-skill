import re

from sqlalchemy.orm import selectinload

from database import db
from exceptions import AuthenticationError, AuthorizationError, ConflictError, NotFoundError, ValidationError
from models.user import User
from services.auth_service import issue_token


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_ROLES = {"user", "admin", "manager"}


class UserService:
    @staticmethod
    def list_all():
        users = db.session.execute(
            db.select(User).options(selectinload(User.tasks))
        ).scalars().all()
        return [{**user.to_dict(), "task_count": len(user.tasks)} for user in users]

    @staticmethod
    def get(user_id):
        user = db.session.execute(
            db.select(User).where(User.id == user_id).options(selectinload(User.tasks))
        ).scalar_one_or_none()
        if not user:
            raise NotFoundError("Usuário não encontrado")
        return {**user.to_dict(), "tasks": [task.to_dict() for task in user.tasks]}

    def create(self, payload):
        values = self._validate(payload, creating=True)
        user = User(name=values["name"], email=values["email"], role="user")
        user.set_password(values["password"])
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    def update(self, user_id, payload, actor):
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        if actor.id != user.id and not actor.is_admin():
            raise AuthorizationError("Operação não autorizada")
        values = self._validate(payload, creating=False, current_user_id=user_id)
        if "role" in values and not actor.is_admin():
            raise AuthorizationError("Somente administradores alteram roles")
        for key, value in values.items():
            if key == "password": user.set_password(value)
            else: setattr(user, key, value)
        db.session.commit()
        return user.to_dict()

    @staticmethod
    def delete(user_id, actor):
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        if actor.id != user.id and not actor.is_admin():
            raise AuthorizationError("Operação não autorizada")
        db.session.delete(user)
        db.session.commit()
        return {"message": "Usuário deletado com sucesso"}

    @staticmethod
    def login(payload):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
        user = db.session.execute(
            db.select(User).where(User.email == str(payload.get("email", "")).lower())
        ).scalar_one_or_none()
        if not user or not user.check_password(str(payload.get("password", ""))):
            raise AuthenticationError("Credenciais inválidas")
        if not user.active:
            raise AuthorizationError("Usuário inativo")
        return {"message": "Login realizado com sucesso", "user": user.to_dict(), "token": issue_token(user)}

    @staticmethod
    def _validate(payload, creating, current_user_id=None):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
        values = {}
        if creating or "name" in payload:
            name = str(payload.get("name", "")).strip()
            if not name: raise ValidationError("Nome é obrigatório")
            values["name"] = name
        if creating or "email" in payload:
            email = str(payload.get("email", "")).strip().lower()
            if not EMAIL_PATTERN.match(email): raise ValidationError("Email inválido")
            existing = db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none()
            if existing and existing.id != current_user_id:
                raise ConflictError("Email já cadastrado")
            values["email"] = email
        if creating or "password" in payload:
            password = str(payload.get("password", ""))
            if len(password) < 8: raise ValidationError("Senha deve ter no mínimo 8 caracteres")
            values["password"] = password
        if "role" in payload:
            if payload["role"] not in VALID_ROLES: raise ValidationError("Role inválido")
            values["role"] = payload["role"]
        if "active" in payload: values["active"] = bool(payload["active"])
        return values
