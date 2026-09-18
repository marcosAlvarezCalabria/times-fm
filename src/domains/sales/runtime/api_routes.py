"""
Endpoints de la API REST para ingesta, pronósticos con TimesFM y gestión de inventario.
"""

from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ..types import (
    BacktestRequest,
    BacktestResult,
    ForecastRequest,
    IngestionSummary,
    NormalizedSeries,
    ProductForecast,
    ReplenishmentRecommendation,
    StoreInventorySummary,
)
from ..config import default_sales_config
from ..service import (
    ForecastService,
    InventoryService,
    NormalizationService,
)

router = APIRouter(prefix="/api", tags=["Sales & TimesFM Forecast"])

# Instancias compartidas dentro de la capa runtime
from ..repository import SalesRepository
_repo = SalesRepository()
_normalization_svc = NormalizationService()
_forecast_svc = ForecastService(repository=_repo)
_inventory_svc = InventoryService(repository=_repo, forecast_service=_forecast_svc)


class HealthResponse(BaseModel):
    status: str
    timesfm_provider: str
    is_mock: bool
    total_products: int


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Estado del servicio y del proveedor TimesFM."""
    provider = _forecast_svc.provider
    return HealthResponse(
        status="operational",
        timesfm_provider=getattr(provider, "model_identifier", "Google TimesFM"),
        is_mock=getattr(provider, "is_mock", True),
        total_products=len(_repo.list_series())
    )


@router.get("/products", response_model=List[NormalizedSeries])
def list_products():
    """Obtiene el catálogo de productos con su historial de ventas registrado."""
    return _repo.list_series()


@router.post("/upload", response_model=IngestionSummary)
async def upload_sales_file(file: UploadFile = File(...)):
    """Ingesta y normaliza un archivo CSV o de texto de ventas (Shopify, TPV, etc.)."""
    try:
        content_bytes = await file.read()
        text_content = content_bytes.decode("utf-8", errors="replace")
        series_list, summary = _normalization_svc.parse_csv_content(text_content)

        for s in series_list:
            _repo.save_series(s)
            if not _repo.get_inventory(s.product_id):
                from ..types import ProductInventory
                _repo.save_inventory(ProductInventory(
                    product_id=s.product_id,
                    product_name=s.product_name,
                    current_stock=int(max(5, s.average_daily_sales * 10)),
                    lead_time_days=7,
                    unit_cost=10.0
                ))
        return summary
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error procesando archivo: {str(exc)}")


@router.post("/load-sample", response_model=IngestionSummary)
def load_sample_dataset():
    """Recarga el dataset de demostración (Café Especialidad & Bakery PYME)."""
    _repo.preload_demo_store()
    series = _repo.list_series()
    first_hist = series[0].history if series else []
    return IngestionSummary(
        total_rows_parsed=len(series) * 90,
        products_count=len(series),
        date_start=first_hist[0].date if first_hist else "",
        date_end=first_hist[-1].date if first_hist else "",
        detected_format="Demo PYME Especialidad",
        sample_products=[s.product_name for s in series]
    )


@router.post("/forecast", response_model=ProductForecast)
def generate_forecast(req: ForecastRequest):
    """Calcula la previsión de ventas y conos de incertidumbre P10/P50/P90."""
    try:
        return _forecast_svc.generate_forecast(
            product_id=req.product_id,
            horizon_days=req.horizon_days,
            quantiles=req.quantiles
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generando forecast: {str(exc)}")


@router.post("/backtest", response_model=BacktestResult)
def run_backtest(req: BacktestRequest):
    """Ejecuta una prueba ciega retrospectiva (Backtesting) sobre los últimos N días."""
    try:
        return _forecast_svc.run_backtest(
            product_id=req.product_id,
            holdout_days=req.holdout_days
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en backtest: {str(exc)}")


@router.get("/inventory/recommendations", response_model=StoreInventorySummary)
def get_inventory_recommendations():
    """Genera recomendaciones de compra y análisis de rotura de stock para toda la tienda."""
    return _inventory_svc.evaluate_store()


@router.get("/inventory/product/{product_id}", response_model=ReplenishmentRecommendation)
def get_product_inventory(product_id: str):
    """Evalúa el estado de stock y punto de reorden de un producto específico."""
    try:
        return _inventory_svc.evaluate_product(product_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Producto no encontrado: {str(exc)}")
