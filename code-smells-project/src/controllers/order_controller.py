from src.exceptions import ValidationError
from src.models.order_model import OrderRepository


VALID_STATUSES = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}


class OrderController:
    def __init__(self, repository=None):
        self.repository = repository or OrderRepository()

    def create(self, payload):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
        user_id = payload.get("usuario_id")
        items = payload.get("itens") or []
        if not user_id:
            raise ValidationError("Usuario ID é obrigatório")
        if not items:
            raise ValidationError("Pedido deve ter pelo menos 1 item")
        result = self.repository.create(user_id, items)
        return {"dados": result, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201

    def list_all(self):
        return {"dados": self.repository.list_all(), "sucesso": True}, 200

    def list_by_user(self, user_id):
        return {"dados": self.repository.list_by_user(user_id), "sucesso": True}, 200

    def update_status(self, order_id, payload):
        status = payload.get("status") if isinstance(payload, dict) else None
        if status not in VALID_STATUSES:
            raise ValidationError("Status inválido")
        self.repository.update_status(order_id, status)
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200

    def sales_report(self):
        return {"dados": self.repository.sales_report(), "sucesso": True}, 200
