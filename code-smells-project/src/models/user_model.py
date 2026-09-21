from werkzeug.security import check_password_hash, generate_password_hash

from src.infrastructure.database import get_db


PUBLIC_COLUMNS = "id, nome, email, tipo, criado_em"


class UserRepository:
    @staticmethod
    def _serialize(row):
        return dict(row) if row else None

    def list_all(self):
        rows = get_db().execute(f"SELECT {PUBLIC_COLUMNS} FROM usuarios").fetchall()
        return [self._serialize(row) for row in rows]

    def get(self, user_id):
        row = get_db().execute(
            f"SELECT {PUBLIC_COLUMNS} FROM usuarios WHERE id = ?", (user_id,)
        ).fetchone()
        return self._serialize(row)

    def create(self, name, email, password, user_type="cliente"):
        db = get_db()
        cursor = db.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
            (name, email, generate_password_hash(password), user_type),
        )
        db.commit()
        return cursor.lastrowid

    def authenticate(self, email, password):
        row = get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        if not row or not check_password_hash(row["senha_hash"], password):
            return None
        return {key: row[key] for key in ("id", "nome", "email", "tipo")}
