"""
Router de presentación web para servir el Dashboard de TimesFM.
"""

from pathlib import Path
from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse

from ..runtime import create_app

ui_router = APIRouter(tags=["UI Dashboard"])

HTML_FILE_PATH = Path(__file__).resolve().parent / "static" / "index.html"


@ui_router.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Sirve la interfaz visual del dashboard interactivo."""
    if HTML_FILE_PATH.exists():
        with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(
        content="<h2>Dashboard no encontrado en ui/static/index.html</h2>",
        status_code=404
    )


def get_full_application() -> FastAPI:
    """Crea la aplicación unificada con API runtime y vistas UI."""
    app = create_app()
    app.include_router(ui_router)
    return app
