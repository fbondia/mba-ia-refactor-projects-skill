from src.exceptions import NotFoundError, ValidationError
from src.models.product_model import ProductRepository


VALID_CATEGORIES = {
    "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"
}


class ProductController:
    def __init__(self, repository=None):
        self.repository = repository or ProductRepository()

    def list_all(self):
        return {"dados": self.repository.list_all(), "sucesso": True}, 200

    def get(self, product_id):
        product = self.repository.get(product_id)
        if not product:
            raise NotFoundError("Produto não encontrado")
        return {"dados": product, "sucesso": True}, 200

    def create(self, payload):
        product_id = self.repository.create(**self._validate(payload))
        return {"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}, 201

    def update(self, product_id, payload):
        if not self.repository.get(product_id):
            raise NotFoundError("Produto não encontrado")
        self.repository.update(product_id, **self._validate(payload))
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    def delete(self, product_id):
        if not self.repository.get(product_id):
            raise NotFoundError("Produto não encontrado")
        self.repository.delete(product_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200

    def search(self, query):
        try:
            minimum = float(query["preco_min"]) if query.get("preco_min") else None
            maximum = float(query["preco_max"]) if query.get("preco_max") else None
        except (TypeError, ValueError) as exc:
            raise ValidationError("Faixa de preço inválida") from exc
        products = self.repository.search(
            query.get("q", ""), query.get("categoria"), minimum, maximum
        )
        return {"dados": products, "total": len(products), "sucesso": True}, 200

    @staticmethod
    def _validate(payload):
        if not isinstance(payload, dict):
            raise ValidationError("Dados inválidos")
        missing = [name for name in ("nome", "preco", "estoque") if name not in payload]
        if missing:
            labels = {"nome": "Nome", "preco": "Preço", "estoque": "Estoque"}
            raise ValidationError(f"{labels[missing[0]]} é obrigatório")
        name = str(payload["nome"]).strip()
        category = payload.get("categoria", "geral")
        try:
            price = float(payload["preco"])
            stock = int(payload["estoque"])
        except (TypeError, ValueError) as exc:
            raise ValidationError("Preço e estoque devem ser numéricos") from exc
        if not 2 <= len(name) <= 200:
            raise ValidationError("Nome deve ter entre 2 e 200 caracteres")
        if price < 0 or stock < 0:
            raise ValidationError("Preço e estoque não podem ser negativos")
        if category not in VALID_CATEGORIES:
            raise ValidationError("Categoria inválida")
        return {
            "nome": name,
            "descricao": str(payload.get("descricao", "")),
            "preco": price,
            "estoque": stock,
            "categoria": category,
        }
