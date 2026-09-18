"""
Configuración y políticas operativas tipadas para el dominio de ventas.
"""

from typing import List
from pydantic import BaseModel, Field

from ..types import ForecastHorizon


class SalesForecastConfig(BaseModel):
    """Parámetros de configuración para el pronóstico y el dimensionamiento de stock."""
    default_horizon_days: int = Field(default=30)
    allowed_horizons: List[int] = Field(default=[7, 30, 60, 90])
    default_quantiles: List[float] = Field(default=[0.1, 0.5, 0.9])
    
    # Nivel de servicio para stock de seguridad (Z=1.65 => 95% de confianza)
    service_level_z_score: float = Field(default=1.65, description="Factor Z para stock de seguridad")
    
    # Parámetros por defecto para proveedores de PYMEs
    default_lead_time_days: int = Field(default=7, description="Tiempo de entrega en días")
    default_cycle_days: int = Field(default=14, description="Frecuencia normal de pedido en días")
    
    # Factor de sobrestock (más de X días de cobertura)
    overstock_threshold_days: int = Field(default=90)


# Instancia global por defecto
default_sales_config = SalesForecastConfig()
