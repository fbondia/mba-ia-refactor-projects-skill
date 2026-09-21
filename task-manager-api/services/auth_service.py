from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from exceptions import AuthenticationError


TOKEN_SALT = "task-manager-auth-v1"


def issue_token(user):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=TOKEN_SALT)
    return serializer.dumps({"user_id": user.id, "role": user.role})


def verify_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=TOKEN_SALT)
    try:
        return serializer.loads(token, max_age=current_app.config["TOKEN_MAX_AGE"])
    except SignatureExpired as exc:
        raise AuthenticationError("Token expirado") from exc
    except BadSignature as exc:
        raise AuthenticationError("Token inválido") from exc
