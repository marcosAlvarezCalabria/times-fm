"""
Interfaz abstracta del proveedor para Google TimesFM.
Define el contrato para modelos reales y emuladores estadísticos.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TimesFMOutput(BaseModel):
    """Contenedor de salida estandarizado para pronósticos TimesFM."""
    point_forecast: List[float] = Field(description="Predicción puntual esperada (P50)")
    quantiles: Dict[str, List[float]] = Field(
        default_factory=dict,
        description="Mapeo de cuantil (ej. 'p10', 'p50', 'p90') a serie proyectada"
    )
    model_name: str = Field(description="Nombre o identificador del modelo utilizado")
    is_mock: bool = Field(default=False, description="Indica si se usó el emulador local")


class TimesFMProvider(ABC):
    """Protocolo base para integración de Google TimesFM."""

    @abstractmethod
    def forecast(
        self,
        history: List[float],
        horizon_days: int,
        quantiles: Optional[List[float]] = None
    ) -> TimesFMOutput:
        """
        Calcula el pronóstico zero-shot para una serie temporal univariada.

        Args:
            history: Historial cronológico de valores (ventas/cantidades diarias).
            horizon_days: Número de días futuros a proyectar (7, 30, 60, 90).
            quantiles: Lista de cuantiles solicitados (ej. [0.1, 0.5, 0.9]).

        Returns:
            TimesFMOutput con la predicción puntual y las bandas de cuantiles.
        """
        pass
