"""
Fábrica del servidor FastAPI para la aplicación de pronósticos con TimesFM.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api_routes import router as sales_api_router


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI con rutas y middleware."""
    app = FastAPI(
        title="TimesFM Sales & Inventory Forecast API",
        description="API para PYMEs: predicción zero-shot con Google TimesFM y gestión de inventario.",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registrar rutas del dominio
    app.include_router(sales_api_router)

    # Montar archivos estáticos de la UI si existen
    ui_static_dir = Path(__file__).resolve().parent.parent / "ui" / "static"
    if ui_static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(ui_static_dir)), name="static")

    return app
