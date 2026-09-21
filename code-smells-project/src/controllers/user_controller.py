from src.exceptions import AuthenticationError, NotFoundError, ValidationError
from src.models.user_model import UserRepository


class UserController:
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def list_all(self):
        return {"dados": self.repository.list_all(), "sucesso": True}, 200

    def get(self, user_id):
        user = self.repository.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        return {"dados": user, "sucesso": True}, 200

    def create(self, payload):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
        name = str(payload.get("nome", "")).strip()
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("senha", ""))
        if not name or not email or not password:
            raise ValidationError("Nome, email e senha são obrigatórios")
        if len(password) < 8:
            raise ValidationError("Senha deve ter no mínimo 8 caracteres")
        user_id = self.repository.create(name, email, password)
        return {"dados": {"id": user_id}, "sucesso": True}, 201

    def login(self, payload):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("senha", ""))
        if not email or not password:
            raise ValidationError("Email e senha são obrigatórios")
        user = self.repository.authenticate(email, password)
        if not user:
            raise AuthenticationError("Email ou senha inválidos")
        return {"dados": user, "sucesso": True, "mensagem": "Login OK"}, 200
