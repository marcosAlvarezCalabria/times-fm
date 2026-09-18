"""
Repositorio en memoria para series históricas de ventas, catálogos e inventario.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math
import random

from ..types import (
    DailySalesPoint,
    NormalizedSeries,
    ProductForecast,
    ProductInventory,
)
from ..config import SalesForecastConfig, default_sales_config


class SalesRepository:
    """Almacén desacoplado en memoria con capacidades de precarga de datasets."""

    def __init__(self, config: Optional[SalesForecastConfig] = None):
        self.config = config or default_sales_config
        self._series: Dict[str, NormalizedSeries] = {}
        self._inventory: Dict[str, ProductInventory] = {}
        self._forecasts: Dict[str, ProductForecast] = {}
        self.preload_demo_store()

    def save_series(self, series: NormalizedSeries) -> None:
        """Guarda o actualiza una serie temporal normalizada."""
        self._series[series.product_id] = series

    def get_series(self, product_id: str) -> Optional[NormalizedSeries]:
        """Obtiene la serie temporal de un producto."""
        return self._series.get(product_id)

    def list_series(self) -> List[NormalizedSeries]:
        """Lista todas las series temporales cargadas."""
        return list(self._series.values())

    def save_inventory(self, inventory: ProductInventory) -> None:
        """Guarda o actualiza los datos de inventario de un producto."""
        self._inventory[inventory.product_id] = inventory

    def get_inventory(self, product_id: str) -> Optional[ProductInventory]:
        """Obtiene el inventario de un producto."""
        return self._inventory.get(product_id)

    def list_inventory(self) -> List[ProductInventory]:
        """Lista todos los registros de inventario."""
        return list(self._inventory.values())

    def save_forecast(self, forecast: ProductForecast) -> None:
        """Cachea el último pronóstico generado para un producto."""
        key = f"{forecast.product_id}_{forecast.horizon_days}"
        self._forecasts[key] = forecast

    def get_forecast(self, product_id: str, horizon_days: int) -> Optional[ProductForecast]:
        """Obtiene un pronóstico cacheado."""
        return self._forecasts.get(f"{product_id}_{horizon_days}")

    def clear(self) -> None:
        """Limpia todos los datos almacenados."""
        self._series.clear()
        self._inventory.clear()
        self._forecasts.clear()

    def preload_demo_store(self) -> None:
        """Precarga datos realistas de muestra para una PYME (Café & Bakery)."""
        self.clear()
        base_date = datetime.now().date() - timedelta(days=90)
        
        products = [
            {"id": "CAFE-ETIOPIA", "name": "Café Grano Especialidad Etiopía 250g", "base": 24, "stock": 42, "lead": 7, "cost": 6.5},
            {"id": "MATCHA-UJI", "name": "Matcha Ceremonial Uji 100g", "base": 12, "stock": 14, "lead": 10, "cost": 12.0},
            {"id": "CROISSANT-FR", "name": "Croissant Francés Mantequilla", "base": 65, "stock": 80, "lead": 2, "cost": 0.8},
            {"id": "MUG-CERAMICA", "name": "Taza Artesanal Cerámica", "base": 5, "stock": 120, "lead": 14, "cost": 4.2},
        ]

        for p in products:
            history: List[DailySalesPoint] = []
            total_u = 0.0
            total_rev = 0.0

            for d in range(90):
                curr = base_date + timedelta(days=d)
                # Estacionalidad fin de semana + tendencia leve + ruido
                dow = curr.weekday()
                weekend_boost = 1.45 if dow in (4, 5, 6) else 0.9
                trend = 1.0 + (d / 90.0) * 0.20
                noise = random.uniform(0.85, 1.18)
                units = max(0.0, round(p["base"] * weekend_boost * trend * noise, 1))
                rev = round(units * (p["cost"] * 2.2), 2)
                
                history.append(DailySalesPoint(
                    date=curr.strftime("%Y-%m-%d"),
                    units_sold=units,
                    revenue=rev
                ))
                total_u += units
                total_rev += rev

            self.save_series(NormalizedSeries(
                product_id=p["id"],
                product_name=p["name"],
                history=history,
                total_units=round(total_u, 1),
                total_revenue=round(total_rev, 2),
                average_daily_sales=round(total_u / 90.0, 2)
            ))

            self.save_inventory(ProductInventory(
                product_id=p["id"],
                product_name=p["name"],
                current_stock=p["stock"],
                lead_time_days=p["lead"],
                unit_cost=p["cost"]
            ))
