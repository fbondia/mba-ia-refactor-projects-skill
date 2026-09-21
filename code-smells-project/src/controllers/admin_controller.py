from src.infrastructure.database import get_db


class AdminController:
    @staticmethod
    def reset_database():
        db = get_db()
        try:
            db.execute("BEGIN")
            for table in ("itens_pedido", "pedidos", "produtos", "usuarios"):
                db.execute(f"DELETE FROM {table}")
            db.commit()
        except Exception:
            db.rollback()
            raise
        return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200

    @staticmethod
    def deprecated_query_endpoint():
        return {"erro": "Endpoint removido por segurança", "sucesso": False}, 410
