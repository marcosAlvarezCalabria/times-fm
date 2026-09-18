"""
Exportación de configuración del dominio de ventas.
"""

from .sales_config import SalesForecastConfig, default_sales_config

__all__ = [
    "SalesForecastConfig",
    "default_sales_config",
]
