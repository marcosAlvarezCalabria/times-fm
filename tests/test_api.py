"""
Pruebas de integración de la API REST FastAPI.
"""

import unittest
from fastapi.testclient import TestClient
from src.domains.sales.ui import get_full_application


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = get_full_application()
        self.client = TestClient(self.app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "operational")

    def test_products_endpoint(self):
        response = self.client.get("/api/products")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_forecast_endpoint(self):
        products = self.client.get("/api/products").json()
        self.assertTrue(len(products) > 0)
        p_id = products[0]["product_id"]

        payload = {"product_id": p_id, "horizon_days": 30}
        response = self.client.post("/api/forecast", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["product_id"], p_id)
        self.assertEqual(len(data["points"]), 30)

    def test_backtest_endpoint(self):
        products = self.client.get("/api/products").json()
        self.assertTrue(len(products) > 0)
        p_id = products[0]["product_id"]

        payload = {"product_id": p_id, "holdout_days": 7}
        response = self.client.post("/api/backtest", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["product_id"], p_id)
        self.assertEqual(data["holdout_days"], 7)
        self.assertEqual(len(data["points"]), 7)
        self.assertGreaterEqual(data["accuracy_pct"], 0.0)
        self.assertGreaterEqual(data["coverage_pct"], 0.0)

    def test_inventory_recommendations_endpoint(self):
        response = self.client.get("/api/inventory/recommendations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("recommendations", data)

    def test_ui_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("TimesFM Sales Forecast", response.text)


if __name__ == "__main__":
    unittest.main()
