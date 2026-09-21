from collections import OrderedDict

from src.exceptions import NotFoundError, ValidationError
from src.infrastructure.database import get_db


DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))


class OrderRepository:
    def create(self, user_id, items):
        db = get_db()
        try:
            db.execute("BEGIN")
            if not db.execute("SELECT 1 FROM usuarios WHERE id = ?", (user_id,)).fetchone():
                raise NotFoundError("Usuário não encontrado")
            normalized = []
            total = 0.0
            for item in items:
                product_id = item.get("produto_id") if isinstance(item, dict) else None
                try:
                    quantity = int(item.get("quantidade", 0))
                except (AttributeError, TypeError, ValueError) as exc:
                    raise ValidationError("Quantidade inválida") from exc
                if quantity <= 0:
                    raise ValidationError("Quantidade deve ser positiva")
                product = db.execute(
                    "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (product_id,)
                ).fetchone()
                if not product:
                    raise NotFoundError(f"Produto {product_id} não encontrado")
                if product["estoque"] < quantity:
                    raise ValidationError(f"Estoque insuficiente para {product['nome']}")
                normalized.append((product, quantity))
                total += product["preco"] * quantity

            cursor = db.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                (user_id, total),
            )
            order_id = cursor.lastrowid
            for product, quantity in normalized:
                db.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                    (order_id, product["id"], quantity, product["preco"]),
                )
                updated = db.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                    (quantity, product["id"], quantity),
                )
                if updated.rowcount != 1:
                    raise ValidationError(f"Estoque insuficiente para {product['nome']}")
            db.commit()
            return {"pedido_id": order_id, "total": total}
        except Exception:
            db.rollback()
            raise

    def list_all(self):
        return self._list()

    def list_by_user(self, user_id):
        return self._list("WHERE p.usuario_id = ?", (user_id,))

    def _list(self, where="", params=()):
        rows = get_db().execute(
            f"""
            SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                   i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido i ON i.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = i.produto_id
            {where}
            ORDER BY p.id, i.id
            """,
            params,
        ).fetchall()
        orders = OrderedDict()
        for row in rows:
            order = orders.setdefault(
                row["id"],
                {
                    "id": row["id"],
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": [],
                },
            )
            if row["produto_id"] is not None:
                order["itens"].append(
                    {
                        "produto_id": row["produto_id"],
                        "produto_nome": row["produto_nome"],
                        "quantidade": row["quantidade"],
                        "preco_unitario": row["preco_unitario"],
                    }
                )
        return list(orders.values())

    def update_status(self, order_id, status):
        db = get_db()
        updated = db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, order_id))
        if updated.rowcount != 1:
            raise NotFoundError("Pedido não encontrado")
        db.commit()

    def sales_report(self):
        row = get_db().execute(
            """
            SELECT COUNT(*) AS total_pedidos, COALESCE(SUM(total), 0) AS faturamento,
                   COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pendentes,
                   COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
                   COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS cancelados
            FROM pedidos
            """
        ).fetchone()
        revenue = row["faturamento"]
        discount_rate = next((rate for limit, rate in DISCOUNT_TIERS if revenue > limit), 0)
        discount = revenue * discount_rate
        count = row["total_pedidos"]
        return {
            "total_pedidos": count,
            "faturamento_bruto": round(revenue, 2),
            "desconto_aplicavel": round(discount, 2),
            "faturamento_liquido": round(revenue - discount, 2),
            "pedidos_pendentes": row["pendentes"],
            "pedidos_aprovados": row["aprovados"],
            "pedidos_cancelados": row["cancelados"],
            "ticket_medio": round(revenue / count, 2) if count else 0,
        }
