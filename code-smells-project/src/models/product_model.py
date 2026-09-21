from src.infrastructure.database import get_db


class ProductRepository:
    @staticmethod
    def _serialize(row):
        return dict(row) if row else None

    def list_all(self):
        return [self._serialize(row) for row in get_db().execute("SELECT * FROM produtos").fetchall()]

    def get(self, product_id):
        row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()
        return self._serialize(row)

    def create(self, nome, descricao, preco, estoque, categoria):
        db = get_db()
        cursor = db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        db.commit()
        return cursor.lastrowid

    def update(self, product_id, nome, descricao, preco, estoque, categoria):
        db = get_db()
        db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, product_id),
        )
        db.commit()

    def delete(self, product_id):
        db = get_db()
        db.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        db.commit()

    def search(self, term, category=None, minimum=None, maximum=None):
        clauses = ["(nome LIKE ? OR descricao LIKE ?)"]
        like = f"%{term}%"
        params = [like, like]
        if category:
            clauses.append("categoria = ?")
            params.append(category)
        if minimum is not None:
            clauses.append("preco >= ?")
            params.append(minimum)
        if maximum is not None:
            clauses.append("preco <= ?")
            params.append(maximum)
        rows = get_db().execute(
            f"SELECT * FROM produtos WHERE {' AND '.join(clauses)}", params
        ).fetchall()
        return [self._serialize(row) for row in rows]
