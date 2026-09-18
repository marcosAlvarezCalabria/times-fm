"""
Pruebas unitarias para el motor de inventario y recomendaciones de reposición.
"""

import unittest
from src.domains.sales.types import ProductInventory, StockoutRiskLevel
from src.domains.sales.repository import SalesRepository
from src.domains.sales.service import ForecastService, InventoryService
from src.providers.timesfm import LocalTimesFMMockProvider


class TestInventoryService(unittest.TestCase):

    def setUp(self):
        self.repo = SalesRepository()
        self.provider = LocalTimesFMMockProvider()
        self.forecast_svc = ForecastService(repository=self.repo, provider=self.provider)
        self.inventory_svc = InventoryService(
            repository=self.repo,
            forecast_service=self.forecast_svc
        )

    def test_evaluate_product_critical_risk(self):
        # Configurar un producto con stock crítico (0 unidades)
        self.repo.save_inventory(ProductInventory(
            product_id="CAFE-ETIOPIA",
            product_name="Café Etiopía",
            current_stock=0,
            lead_time_days=7,
            unit_cost=6.5
        ))
        rec = self.inventory_svc.evaluate_product("CAFE-ETIOPIA")
        self.assertEqual(rec.risk_level, StockoutRiskLevel.CRITICAL)
        self.assertGreater(rec.recommended_order_units, 0)
        self.assertGreater(rec.estimated_order_cost, 0.0)

    def test_evaluate_store_summary(self):
        summary = self.inventory_svc.evaluate_store()
        self.assertGreater(summary.total_products_tracked, 0)
        self.assertEqual(len(summary.recommendations), summary.total_products_tracked)


if __name__ == "__main__":
    unittest.main()
