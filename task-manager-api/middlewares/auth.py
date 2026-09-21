from functools import wraps

from flask import g, request

from database import db
from exceptions import AuthenticationError, AuthorizationError
from models.user import User
from services.auth_service import verify_token


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise AuthenticationError("Autenticação obrigatória")
        claims = verify_token(header[7:])
        user = db.session.get(User, claims["user_id"])
        if not user or not user.active:
            raise AuthenticationError("Usuário inválido")
        g.current_user = user
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @login_required
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.current_user.is_admin():
            raise AuthorizationError("Acesso administrativo negado")
        return view(*args, **kwargs)
    return wrapped
