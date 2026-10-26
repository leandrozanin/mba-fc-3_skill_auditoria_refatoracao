import tempfile
import unittest
from pathlib import Path

from app import create_app


class ECommerceApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "DATABASE": str(Path(self.temp_dir.name) / "test.db"),
            "SECRET_KEY": "test-only-secret",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_returns_status_without_operational_secrets(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")
        for sensitive_key in ("secret_key", "db_path", "debug"):
            self.assertNotIn(sensitive_key, response.json)

    def test_admin_query_is_retired(self):
        response = self.client.post("/admin/query", json={"sql": "SELECT 1"})

        self.assertEqual(response.status_code, 410)

    def test_database_reset_is_disabled(self):
        response = self.client.post("/admin/reset-db")

        self.assertEqual(response.status_code, 403)

    def test_user_listing_never_returns_passwords_or_hashes(self):
        response = self.client.get("/usuarios")

        self.assertEqual(response.status_code, 200)
        for user in response.json["dados"]:
            self.assertNotIn("senha", user)
            self.assertNotIn("password", user)

    def test_product_with_apostrophe_can_be_created_and_read(self):
        created = self.client.post("/produtos", json={
            "nome": "Produto d'Água",
            "preco": 1.5,
            "estoque": 2,
            "categoria": "geral",
        })

        self.assertEqual(created.status_code, 201)
        product_id = created.json["dados"]["id"]
        fetched = self.client.get(f"/produtos/{product_id}")
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json["dados"]["nome"], "Produto d'Água")

    def test_search_treats_sql_metacharacters_as_plain_text(self):
        response = self.client.get("/produtos/busca", query_string={"q": "' OR 1=1 --"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["dados"], [])

    def test_login_with_missing_body_returns_client_error(self):
        response = self.client.post("/login", json=None)

        self.assertEqual(response.status_code, 400)

    def test_negative_order_quantity_is_rejected(self):
        response = self.client.post("/pedidos", json={
            "usuario_id": 1,
            "itens": [{"produto_id": 1, "quantidade": -1}],
        })

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()

