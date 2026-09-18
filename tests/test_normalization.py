"""
Pruebas unitarias para el servicio de normalización de ventas.
"""

import unittest
from src.domains.sales.service import NormalizationService


class TestNormalizationService(unittest.TestCase):

    def setUp(self):
        self.service = NormalizationService()

    def test_parse_shopify_format(self):
        csv_data = """Created at,Lineitem name,Lineitem quantity,Total Sales
2026-01-01,Café Etiopía,2,24.00
2026-01-02,Café Etiopía,4,48.00
2026-01-04,Café Etiopía,3,36.00
"""
        series_list, summary = self.service.parse_csv_content(csv_data)
        self.assertEqual(len(series_list), 1)
        self.assertEqual(summary.products_count, 1)
        # Debe haber imputado el día 2026-01-03 con 0 ventas
        cafe_series = series_list[0]
        self.assertEqual(len(cafe_series.history), 4)
        dates = [p.date for p in cafe_series.history]
        self.assertIn("2026-01-03", dates)
        p_03 = next(p for p in cafe_series.history if p.date == "2026-01-03")
        self.assertEqual(p_03.units_sold, 0.0)

    def test_parse_generic_format(self):
        csv_data = """Date,Product,Qty,Revenue
2026-02-10,Item A,10,100.0
2026-02-11,Item B,5,50.0
"""
        series_list, summary = self.service.parse_csv_content(csv_data)
        self.assertEqual(len(series_list), 2)
        self.assertEqual(summary.products_count, 2)


if __name__ == "__main__":
    unittest.main()
