"""
Pruebas unitarias para los proveedores de Google TimesFM y Mock.
"""

import unittest
from src.providers.timesfm import LocalTimesFMMockProvider, get_timesfm_provider


class TestTimesFMProviders(unittest.TestCase):

    def setUp(self):
        self.mock_provider = LocalTimesFMMockProvider()
        self.sample_history = [12.0, 15.0, 14.0, 18.0, 25.0, 30.0, 22.0] * 4  # 28 días

    def test_forecast_output_structure(self):
        output = self.mock_provider.forecast(
            history=self.sample_history,
            horizon_days=30,
            quantiles=[0.1, 0.5, 0.9]
        )
        self.assertEqual(len(output.point_forecast), 30)
        self.assertIn("p10", output.quantiles)
        self.assertIn("p50", output.quantiles)
        self.assertIn("p90", output.quantiles)
        self.assertEqual(len(output.quantiles["p10"]), 30)
        self.assertEqual(len(output.quantiles["p90"]), 30)

    def test_quantile_ordering(self):
        """P10 <= P50 <= P90 para cada paso del horizonte."""
        output = self.mock_provider.forecast(
            history=self.sample_history,
            horizon_days=14,
            quantiles=[0.1, 0.5, 0.9]
        )
        p10 = output.quantiles["p10"]
        p50 = output.quantiles["p50"]
        p90 = output.quantiles["p90"]

        for i in range(14):
            self.assertLessEqual(p10[i], p50[i] + 1e-4)
            self.assertLessEqual(p50[i], p90[i] + 1e-4)
            self.assertGreaterEqual(p10[i], 0.0)

    def test_factory_fallback(self):
        provider = get_timesfm_provider(force_mock=True)
        self.assertIsNotNone(provider)


if __name__ == "__main__":
    unittest.main()
