"""
Tipos de datos y DTOs para análisis de inventario, stockout y reposición.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class StockoutRiskLevel(str, Enum):
    """Nivel de urgencia o riesgo de rotura de stock."""
    CRITICAL = "CRITICAL"      # Rotura antes de que llegue el pedido (Lead Time)
    WARNING = "WARNING"        # Stock por debajo del punto de reorden (ROP)
    OPTIMAL = "OPTIMAL"        # Stock balanceado para el ciclo de venta
    OVERSTOCKED = "OVERSTOCKED"# Exceso de stock por encima del horizonte de 90 días


class ProductInventory(BaseModel):
    """Información de stock y parámetros de reposición de un producto."""
    product_id: str
    product_name: str
    current_stock: int = Field(ge=0, description="Unidades físicas disponibles")
    lead_time_days: int = Field(default=7, ge=1, description="Días que tarda el proveedor")
    unit_cost: float = Field(default=10.0, ge=0.0, description="Coste unitario de reposición")
    safety_stock: Optional[float] = Field(default=None, description="Stock de seguridad calculado")


class ReplenishmentRecommendation(BaseModel):
    """Recomendación accionable generada por el motor de inventario."""
    product_id: str
    product_name: str
    current_stock: int
    lead_time_days: int
    unit_cost: float
    days_of_inventory: float = Field(description="Días de cobertura según demanda P50")
    reorder_point: float = Field(description="Punto de reorden (ROP)")
    runout_date: Optional[str] = Field(default=None, description="Fecha estimada de rotura")
    recommended_order_units: int = Field(description="Unidades sugeridas para ordenar")
    estimated_order_cost: float = Field(description="Inversión requerida en euros/divisa")
    risk_level: StockoutRiskLevel
    justification: str


class StoreInventorySummary(BaseModel):
    """Visión global de inventario de la tienda."""
    total_products_tracked: int
    critical_count: int
    warning_count: int
    optimal_count: int
    overstocked_count: int
    total_reorder_budget_needed: float
    recommendations: List[ReplenishmentRecommendation]
