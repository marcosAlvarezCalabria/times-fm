"""
Motor de optimización de inventario, detección de rotura de stock y reposición.
"""

from datetime import datetime, timedelta
import math
from typing import List, Optional

from ..types import (
    ProductInventory,
    ReplenishmentRecommendation,
    StockoutRiskLevel,
    StoreInventorySummary,
)
from ..config import SalesForecastConfig, default_sales_config
from ..repository import SalesRepository
from .forecast_service import ForecastService


class InventoryService:
    """Calcula el riesgo de desabastecimiento y sugiere órdenes de compra inteligentes."""

    def __init__(
        self,
        repository: SalesRepository,
        forecast_service: ForecastService,
        config: Optional[SalesForecastConfig] = None
    ):
        self.repository = repository
        self.forecast_service = forecast_service
        self.config = config or default_sales_config

    def evaluate_product(self, product_id: str) -> ReplenishmentRecommendation:
        inv = self.repository.get_inventory(product_id)
        series = self.repository.get_series(product_id)
        name = series.product_name if series else (inv.product_name if inv else product_id)

        current_stock = inv.current_stock if inv else 10
        lead_time = inv.lead_time_days if inv else self.config.default_lead_time_days
        cost = inv.unit_cost if inv else 10.0

        # Obtener o calcular pronóstico a 30 días
        forecast = self.repository.get_forecast(product_id, 30)
        if not forecast:
            forecast = self.forecast_service.generate_forecast(product_id, 30)

        # 1. Demanda diaria promedio P50 y P90
        d_p50 = forecast.expected_total_demand / 30.0
        d_p90 = forecast.p90_total_demand / 30.0
        daily_rate = max(0.1, d_p50)

        # 2. Días de inventario restantes (DOI)
        doi = round(current_stock / daily_rate, 1)

        # 3. Stock de seguridad (SS) y Punto de reorden (ROP)
        # SS cubre la variabilidad P90-P50 durante el plazo de entrega
        safety_stock = round(max(2.0, (d_p90 - d_p50) * math.sqrt(lead_time) * 1.2), 1)
        lead_time_demand = d_p50 * lead_time
        reorder_point = round(lead_time_demand + safety_stock, 1)

        # 4. Proyección de fecha de rotura de stock (Runout Date)
        runout_date: Optional[str] = None
        accumulated = 0.0
        for pt in forecast.points:
            accumulated += pt.p50
            if accumulated >= current_stock:
                runout_date = pt.date
                break

        # 5. Determinación de nivel de riesgo
        cycle_days = self.config.default_cycle_days
        target_stock = (lead_time + cycle_days) * d_p50 + safety_stock
        needed_units = max(0, int(math.ceil(target_stock - current_stock)))

        if doi <= lead_time or current_stock == 0:
            risk = StockoutRiskLevel.CRITICAL
            justification = (
                f"¡RIESGO CRÍTICO! Stock para {doi} días, pero el proveedor tarda {lead_time} días. "
                f"Rotura estimada el {runout_date or 'pronto'}. Pedir urgente {needed_units} uds."
            )
        elif current_stock <= reorder_point:
            risk = StockoutRiskLevel.WARNING
            justification = (
                f"Stock ({current_stock} uds) por debajo del punto de reorden ({reorder_point} uds). "
                f"Emitir orden de compra para el siguiente ciclo ({needed_units} uds)."
            )
        elif doi > self.config.overstock_threshold_days:
            risk = StockoutRiskLevel.OVERSTOCKED
            needed_units = 0
            justification = f"Sobrestock detectado: {doi} días de cobertura estimada. No reponer."
        else:
            risk = StockoutRiskLevel.OPTIMAL
            needed_units = 0
            justification = f"Nivel saludable de stock ({current_stock} uds). Cobertura estimada: {doi} días."

        return ReplenishmentRecommendation(
            product_id=product_id,
            product_name=name,
            current_stock=current_stock,
            lead_time_days=lead_time,
            unit_cost=cost,
            days_of_inventory=doi,
            reorder_point=reorder_point,
            runout_date=runout_date,
            recommended_order_units=needed_units,
            estimated_order_cost=round(needed_units * cost, 2),
            risk_level=risk,
            justification=justification
        )

    def evaluate_store(self) -> StoreInventorySummary:
        """Evalúa todos los productos activos y consolida el resumen de la tienda."""
        all_series = self.repository.list_series()
        recommendations = [self.evaluate_product(s.product_id) for s in all_series]

        critical = sum(1 for r in recommendations if r.risk_level == StockoutRiskLevel.CRITICAL)
        warning = sum(1 for r in recommendations if r.risk_level == StockoutRiskLevel.WARNING)
        optimal = sum(1 for r in recommendations if r.risk_level == StockoutRiskLevel.OPTIMAL)
        overstocked = sum(1 for r in recommendations if r.risk_level == StockoutRiskLevel.OVERSTOCKED)
        total_budget = round(sum(r.estimated_order_cost for r in recommendations), 2)

        return StoreInventorySummary(
            total_products_tracked=len(recommendations),
            critical_count=critical,
            warning_count=warning,
            optimal_count=optimal,
            overstocked_count=overstocked,
            total_reorder_budget_needed=total_budget,
            recommendations=recommendations
        )
