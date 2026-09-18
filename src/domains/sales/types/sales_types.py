"""
Tipos de datos y DTOs para registros de venta e ingesta de series temporales.
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SalesRecord(BaseModel):
    """Representa una línea transaccional de venta parseada."""
    sale_date: str = Field(description="Fecha de la venta en formato YYYY-MM-DD")
    product_id: str = Field(description="Identificador único o SKU del producto")
    product_name: str = Field(description="Nombre descriptivo del producto")
    units_sold: float = Field(ge=0.0, description="Cantidad de unidades vendidas")
    revenue: float = Field(ge=0.0, description="Ingresos totales generados por la venta")
    unit_price: Optional[float] = Field(default=None, description="Precio unitario de venta")


class DailySalesPoint(BaseModel):
    """Punto diario consolidado para análisis de series temporales."""
    date: str = Field(description="Fecha (YYYY-MM-DD)")
    units_sold: float = Field(ge=0.0, description="Unidades totales del día")
    revenue: float = Field(ge=0.0, description="Ingresos totales del día")


class NormalizedSeries(BaseModel):
    """Serie temporal regularizada y lista para inferencia con TimesFM."""
    product_id: str
    product_name: str
    history: List[DailySalesPoint]
    total_units: float = 0.0
    total_revenue: float = 0.0
    average_daily_sales: float = 0.0


class IngestionSummary(BaseModel):
    """Resumen informativo del proceso de carga y normalización de datos."""
    total_rows_parsed: int
    products_count: int
    date_start: str
    date_end: str
    detected_format: str
    sample_products: List[str]
