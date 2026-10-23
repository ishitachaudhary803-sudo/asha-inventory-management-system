import os
import tempfile
import unittest

# Use a temporary database for tests so the demo database is not altered.
test_dir = tempfile.TemporaryDirectory()
os.environ["DATABASE_PATH"] = os.path.join(test_dir.name, "test_inventory.db")

from app import app, init_db

class InventoryAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Product catalogue", response.data)

    def test_health_route(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_seed_products_exist(self):
        response = self.client.get("/api/products")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.get_json()), 3)

    def test_add_product(self):
        response = self.client.post("/api/products", json={
            "name": "Test Item", "sku": "TEST-100", "category": "Test",
            "price": 12.5, "quantity": 4, "description": "Test description"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["sku"], "TEST-100")

    def test_reject_duplicate_sku(self):
        payload = {"name": "First", "sku": "DUP-1", "price": 1, "quantity": 1}
        first = self.client.post("/api/products", json=payload)
        second = self.client.post("/api/products", json={**payload, "name": "Second"})
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)

if __name__ == "__main__":
    unittest.main()
