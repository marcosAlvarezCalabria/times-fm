"""
Exportación de capa runtime para el servidor y rutas de la API.
"""

from .api_routes import router as sales_api_router
from .server import create_app

__all__ = [
    "sales_api_router",
    "create_app",
]
