"""
Tipos de datos y DTOs para pronósticos y cuantiles con Google TimesFM.
"""

from enum import IntEnum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ForecastHorizon(IntEnum):
    """Horizontes estándar soportados para PYMEs."""
    WEEK_1 = 7
    MONTH_1 = 30
    MONTHS_2 = 60
    MONTHS_3 = 90


class ForecastDayPoint(BaseModel):
    """Punto proyectado para un día futuro con bandas de incertidumbre."""
    date: str = Field(description="Fecha proyectada (YYYY-MM-DD)")
    day_index: int = Field(description="Índice relativo del día futuro (1..H)")
    p10: float = Field(description="Cuantil 10% (Escenario de baja demanda)")
    p50: float = Field(description="Cuantil 50% (Mediana esperada)")
    p90: float = Field(description="Cuantil 90% (Escenario pesimista para stock)")


class ForecastRequest(BaseModel):
    """Solicitud de pronóstico."""
    product_id: str
    horizon_days: int = Field(default=30, description="Días a proyectar: 7, 30, 60 o 90")
    quantiles: Optional[List[float]] = Field(default=[0.1, 0.5, 0.9])


class ProductForecast(BaseModel):
    """Resultado completo del pronóstico con métricas agregadas."""
    product_id: str
    product_name: str
    horizon_days: int
    model_used: str
    is_mock: bool
    points: List[ForecastDayPoint]
    expected_total_demand: float
    p10_total_demand: float
    p90_total_demand: float
    trend_direction: str = Field(description="'UP', 'DOWN' o 'STABLE'")


class BacktestPoint(BaseModel):
    """Comparación día a día entre venta real y predicción ciega de TimesFM."""
    date: str
    actual_sales: float
    p10: float
    p50: float
    p90: float
    inside_cone: bool
    abs_error: float


class BacktestRequest(BaseModel):
    """Petición de auditoría histórica ciega."""
    product_id: str
    holdout_days: int = Field(default=7, ge=3, le=30)


class BacktestResult(BaseModel):
    """Resultado de la prueba ciega retrospectiva."""
    product_id: str
    product_name: str
    holdout_days: int
    accuracy_pct: float
    coverage_pct: float
    mape: float
    total_actual: float
    total_predicted_p50: float
    points: List[BacktestPoint]
    verdict: str
