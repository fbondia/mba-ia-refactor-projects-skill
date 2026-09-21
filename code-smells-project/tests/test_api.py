import os
import tempfile
import unittest

os.environ.setdefault("SECRET_KEY", "test-secret-not-for-production")

from src.app import create_app


class EcommerceApiTest(unittest.TestCase):
    def setUp(self):
        handle, self.database = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": self.database,
                "SECRET_KEY": "test-secret-not-for-production",
                "ADMIN_TOKEN": "test-admin-token",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.database)

    def test_original_endpoint_matrix(self):
        checks = [
            self.client.get("/"), self.client.get("/produtos"),
            self.client.get("/produtos/busca?q=Mouse"), self.client.get("/produtos/1"),
            self.client.get("/usuarios"), self.client.get("/usuarios/1"),
            self.client.get("/pedidos"), self.client.get("/pedidos/usuario/1"),
            self.client.get("/relatorios/vendas"), self.client.get("/health"),
        ]
        self.assertTrue(all(response.status_code == 200 for response in checks))

    def test_product_crud_and_validation(self):
        created = self.client.post(
            "/produtos", json={"nome": "Livro", "preco": 50, "estoque": 3, "categoria": "livros"}
        )
        self.assertEqual(created.status_code, 201)
        product_id = created.get_json()["dados"]["id"]
        updated = self.client.put(
            f"/produtos/{product_id}",
            json={"nome": "Livro 2", "preco": 60, "estoque": 2, "categoria": "livros"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.delete(f"/produtos/{product_id}").status_code, 200)

    def test_user_login_and_order_transaction(self):
        created = self.client.post(
            "/usuarios", json={"nome": "Teste", "email": "test@example.com", "senha": "strong-pass"}
        )
        user_id = created.get_json()["dados"]["id"]
        self.assertEqual(self.client.post(
            "/login", json={"email": "test@example.com", "senha": "strong-pass"}
        ).status_code, 200)
        order = self.client.post(
            "/pedidos", json={"usuario_id": user_id, "itens": [{"produto_id": 1, "quantidade": 1}]}
        )
        self.assertEqual(order.status_code, 201)
        order_id = order.get_json()["dados"]["pedido_id"]
        self.assertEqual(self.client.put(
            f"/pedidos/{order_id}/status", json={"status": "aprovado"}
        ).status_code, 200)

    def test_admin_security_and_removed_query(self):
        self.assertEqual(self.client.post("/admin/reset-db").status_code, 403)
        self.assertEqual(self.client.post("/admin/query", json={"sql": "SELECT 1"}).status_code, 410)
        response = self.client.get("/health")
        self.assertNotIn("secret", str(response.get_json()).lower())
        self.assertEqual(
            self.client.post(
                "/admin/reset-db", headers={"X-Admin-Token": "test-admin-token"}
            ).status_code,
            200,
        )


if __name__ == "__main__":
    unittest.main()
