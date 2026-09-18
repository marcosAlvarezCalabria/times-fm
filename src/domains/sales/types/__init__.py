"""
Exportación consolidada de tipos y DTOs para el dominio de ventas.
"""

from .sales_types import (
    SalesRecord,
    DailySalesPoint,
    NormalizedSeries,
    IngestionSummary,
)
from .forecast_types import (
    ForecastHorizon,
    ForecastDayPoint,
    ForecastRequest,
    ProductForecast,
    BacktestPoint,
    BacktestRequest,
    BacktestResult,
)
from .inventory_types import (
    StockoutRiskLevel,
    ProductInventory,
    ReplenishmentRecommendation,
    StoreInventorySummary,
)

__all__ = [
    "SalesRecord",
    "DailySalesPoint",
    "NormalizedSeries",
    "IngestionSummary",
    "ForecastHorizon",
    "ForecastDayPoint",
    "ForecastRequest",
    "ProductForecast",
    "BacktestPoint",
    "BacktestRequest",
    "BacktestResult",
    "StockoutRiskLevel",
    "ProductInventory",
    "ReplenishmentRecommendation",
    "StoreInventorySummary",
]
