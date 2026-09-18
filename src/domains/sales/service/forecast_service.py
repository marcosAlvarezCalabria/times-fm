"""
Servicio de orquestación de pronósticos probabilísticos con Google TimesFM y Backtesting.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from ....providers.timesfm import TimesFMProvider, get_timesfm_provider
from ..types import (
    BacktestPoint,
    BacktestResult,
    ForecastDayPoint,
    ForecastHorizon,
    ProductForecast,
)
from ..config import SalesForecastConfig, default_sales_config
from ..repository import SalesRepository


class ForecastService:
    """Orquesta las predicciones temporales, cuantiles y auditorías ciegas con TimesFM."""

    def __init__(
        self,
        repository: SalesRepository,
        provider: Optional[TimesFMProvider] = None,
        config: Optional[SalesForecastConfig] = None,
    ):
        self.repository = repository
        self.provider = provider or get_timesfm_provider()
        self.config = config or default_sales_config

    def generate_forecast(
        self,
        product_id: str,
        horizon_days: int = 30,
        quantiles: Optional[List[float]] = None
    ) -> ProductForecast:
        """Ejecuta el pronóstico zero-shot con cuantiles P10, P50, P90 para un producto."""
        series = self.repository.get_series(product_id)
        if not series:
            raise ValueError(f"No se encontró serie histórica para el producto: '{product_id}'")

        if horizon_days not in self.config.allowed_horizons:
            horizon_days = self.config.default_horizon_days

        q_list = quantiles or self.config.default_quantiles
        history_values = [p.units_sold for p in series.history]

        output = self.provider.forecast(
            history=history_values,
            horizon_days=horizon_days,
            quantiles=q_list
        )

        last_date_str = series.history[-1].date if series.history else datetime.now().strftime("%Y-%m-%d")
        last_dt = datetime.strptime(last_date_str, "%Y-%m-%d").date()

        p10_series = output.quantiles.get("p10", output.point_forecast)
        p50_series = output.quantiles.get("p50", output.point_forecast)
        p90_series = output.quantiles.get("p90", output.point_forecast)

        forecast_points: List[ForecastDayPoint] = []
        for i in range(horizon_days):
            target_date = last_dt + timedelta(days=i + 1)
            forecast_points.append(ForecastDayPoint(
                date=target_date.strftime("%Y-%m-%d"),
                day_index=i + 1,
                p10=round(p10_series[i], 2),
                p50=round(p50_series[i], 2),
                p90=round(p90_series[i], 2)
            ))

        total_p50 = round(sum(p.p50 for p in forecast_points), 1)
        total_p10 = round(sum(p.p10 for p in forecast_points), 1)
        total_p90 = round(sum(p.p90 for p in forecast_points), 1)

        recent_window = history_values[-14:] if len(history_values) >= 14 else history_values
        recent_avg = sum(recent_window) / max(1, len(recent_window))
        forecast_avg = total_p50 / max(1, horizon_days)

        if forecast_avg > recent_avg * 1.08:
            trend = "UP"
        elif forecast_avg < recent_avg * 0.92:
            trend = "DOWN"
        else:
            trend = "STABLE"

        result = ProductForecast(
            product_id=series.product_id,
            product_name=series.product_name,
            horizon_days=horizon_days,
            model_used=output.model_name,
            is_mock=output.is_mock,
            points=forecast_points,
            expected_total_demand=total_p50,
            p10_total_demand=total_p10,
            p90_total_demand=total_p90,
            trend_direction=trend
        )

        self.repository.save_forecast(result)
        return result

    def run_backtest(self, product_id: str, holdout_days: int = 7) -> BacktestResult:
        """
        Prueba ciega retrospectiva: oculta los últimos N días, predice con TimesFM
        y evalúa la precisión matemática contra las ventas reales ocurridas.
        """
        series = self.repository.get_series(product_id)
        if not series:
            raise ValueError(f"No se encontró serie para el producto: '{product_id}'")

        if len(series.history) < holdout_days + 7:
            raise ValueError(
                f"Se necesitan al menos {holdout_days + 7} días para el backtest (actual: {len(series.history)} días)."
            )

        train_slice = series.history[:-holdout_days]
        test_slice = series.history[-holdout_days:]
        train_values = [p.units_sold for p in train_slice]

        output = self.provider.forecast(
            history=train_values,
            horizon_days=holdout_days,
            quantiles=[0.1, 0.5, 0.9]
        )

        p10_list = output.quantiles.get("p10", output.point_forecast)
        p50_list = output.quantiles.get("p50", output.point_forecast)
        p90_list = output.quantiles.get("p90", output.point_forecast)

        points: List[BacktestPoint] = []
        total_actual = 0.0
        total_predicted = 0.0
        inside_count = 0
        sum_ape = 0.0

        for i in range(holdout_days):
            actual = test_slice[i].units_sold
            p10 = p10_list[i]
            p50 = p50_list[i]
            p90 = p90_list[i]

            # ¿Cayó la venta real dentro de la banda de seguridad P10 - P90?
            inside = (actual >= p10 - 0.5) and (actual <= p90 + 0.5)
            if inside:
                inside_count += 1

            abs_err = abs(actual - p50)
            ape = (abs_err / max(1.0, actual)) if actual > 0 else 0.0
            sum_ape += ape

            total_actual += actual
            total_predicted += p50

            points.append(BacktestPoint(
                date=test_slice[i].date,
                actual_sales=round(actual, 2),
                p10=round(p10, 2),
                p50=round(p50, 2),
                p90=round(p90, 2),
                inside_cone=inside,
                abs_error=round(abs_err, 2)
            ))

        mape = round((sum_ape / max(1, holdout_days)) * 100.0, 1)
        accuracy = max(0.0, round(100.0 - min(100.0, mape), 1))
        coverage = round((inside_count / max(1, holdout_days)) * 100.0, 1)

        if coverage >= 80.0:
            verdict = f"EXCELENTE: El {coverage}% de las ventas reales cayeron exactamente en la banda de confianza P10-P90."
        elif coverage >= 60.0:
            verdict = f"BUENO: El {coverage}% de los días coincidió con la banda proyectada (Precisión P50: {accuracy}%)."
        else:
            verdict = f"MODERADO: Precisión del {accuracy}%. Se aconseja registrar más semanas para mayor estacionalidad."

        return BacktestResult(
            product_id=series.product_id,
            product_name=series.product_name,
            holdout_days=holdout_days,
            accuracy_pct=accuracy,
            coverage_pct=coverage,
            mape=mape,
            total_actual=round(total_actual, 1),
            total_predicted_p50=round(total_predicted, 1),
            points=points,
            verdict=verdict
        )
