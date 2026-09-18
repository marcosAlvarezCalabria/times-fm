"""
Emulador estadístico local de alta fidelidad para Google TimesFM.
Simula el comportamiento zero-shot con descomposición estacional, tendencia y cuantiles.
"""

import math
from typing import Dict, List, Optional
import numpy as np

from .interface import TimesFMOutput, TimesFMProvider


class LocalTimesFMMockProvider(TimesFMProvider):
    """
    Proveedor simulador para desarrollo y testing sin requisitos de GPU.
    Aplica descomposición estacional de 7 días, regresión de tendencia y conos gaussianos.
    """

    def __init__(self, model_identifier: str = "google/timesfm-1.0-200m (Local Emulated)"):
        self.model_identifier = model_identifier

    def forecast(
        self,
        history: List[float],
        horizon_days: int,
        quantiles: Optional[List[float]] = None
    ) -> TimesFMOutput:
        if quantiles is None:
            quantiles = [0.1, 0.5, 0.9]

        if not history:
            zeros = [0.0] * horizon_days
            return TimesFMOutput(
                point_forecast=zeros,
                quantiles={f"p{int(q*100)}": list(zeros) for q in quantiles},
                model_name=self.model_identifier,
                is_mock=True
            )

        arr = np.array(history, dtype=np.float64)
        n = len(arr)

        # 1. Nivel base y tendencia
        if n >= 14:
            x = np.arange(n)
            slope, intercept = np.polyfit(x, arr, 1)
            # Amortiguar la pendiente para evitar extrapolaciones infinitas
            slope = float(np.clip(slope, -0.5, 0.5) * 0.85)
            baseline = float(intercept + slope * n)
        else:
            slope = 0.0
            baseline = float(np.mean(arr))

        # 2. Estacionalidad semanal (7 días)
        dow_weights = np.ones(7, dtype=np.float64)
        if n >= 7:
            for d in range(7):
                indices = [i for i in range(n) if i % 7 == d]
                if indices:
                    dow_weights[d] = max(0.2, float(np.mean(arr[indices]) / (np.mean(arr) + 1e-6)))

        # 3. Varianza de los residuos para las bandas probabilísticas
        residuals = np.diff(arr) if n > 1 else np.array([1.0])
        std_dev = max(1.0, float(np.std(residuals)))

        # Mapeo de factores Z para cuantiles comunes
        z_factors = {
            0.1: -1.282,
            0.5: 0.0,
            0.9: 1.282,
            0.25: -0.674,
            0.75: 0.674
        }

        p50_list: List[float] = []
        quantiles_dict: Dict[str, List[float]] = {f"p{int(q*100)}": [] for q in quantiles}

        for step in range(horizon_days):
            t = n + step
            seasonality = dow_weights[t % 7]
            # Proyección central
            expected = max(0.0, (baseline + slope * step) * seasonality)
            p50_list.append(round(expected, 2))

            # Expansión de la incertidumbre con el horizonte: sqrt(1 + step/14)
            step_uncertainty = std_dev * math.sqrt(1.0 + (step / 14.0))

            for q in quantiles:
                key = f"p{int(q*100)}"
                z = z_factors.get(q, (q - 0.5) * 2.5)
                val = max(0.0, expected + z * step_uncertainty)
                quantiles_dict[key].append(round(float(val), 2))

        return TimesFMOutput(
            point_forecast=p50_list,
            quantiles=quantiles_dict,
            model_name=self.model_identifier,
            is_mock=True
        )
