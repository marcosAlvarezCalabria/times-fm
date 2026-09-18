"""
Integración con Google TimesFM oficial (con fallback automático y transparente a Mock).
"""

import logging
from typing import List, Optional

from .interface import TimesFMOutput, TimesFMProvider
from .mock_provider import LocalTimesFMMockProvider

logger = logging.getLogger(__name__)


class GoogleTimesFMProvider(TimesFMProvider):
    """
    Proveedor productivo de Google TimesFM.
    Si el paquete oficial 'timesfm' o los pesos no están disponibles, activa el fallback emulado.
    """

    def __init__(
        self,
        checkpoint_path: str = "google/timesfm-1.0-200m",
        fallback_enabled: bool = True
    ):
        self.checkpoint_path = checkpoint_path
        self.fallback_enabled = fallback_enabled
        self._tfm_model = None
        self._fallback_provider = LocalTimesFMMockProvider(
            model_identifier=f"{checkpoint_path} (Fallback Activo)"
        )
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Intenta cargar el modelo TimesFM oficial."""
        try:
            # Intento de importación del SDK oficial de Google TimesFM
            import timesfm  # type: ignore
            logger.info("Cargando modelo Google TimesFM desde %s...", self.checkpoint_path)
            self._tfm_model = timesfm.TimesFm(
                context_len=512,
                horizon_len=128,
                input_patch_len=32,
                output_patch_len=128,
                num_layers=20,
                model_dims=1280,
                backend="cpu"
            )
            # Carga de checkpoints
            self._tfm_model.load_from_checkpoint(repo_id=self.checkpoint_path)
            logger.info("Google TimesFM inicializado correctamente.")
        except Exception as exc:
            logger.warning(
                "No se pudo inicializar Google TimesFM nativo (%s). Fallback emulado activado.",
                exc
            )
            self._tfm_model = None

    def forecast(
        self,
        history: List[float],
        horizon_days: int,
        quantiles: Optional[List[float]] = None
    ) -> TimesFMOutput:
        if quantiles is None:
            quantiles = [0.1, 0.5, 0.9]

        # Si el modelo oficial está cargado, lo usamos
        if self._tfm_model is not None:
            try:
                import numpy as np  # type: ignore
                inputs = [np.array(history, dtype=np.float32)]
                point_forecast, q_forecast = self._tfm_model.forecast(
                    inputs,
                    freq=[0]  # Frecuencia diaria
                )
                point_list = [round(float(v), 2) for v in point_forecast[0][:horizon_days]]
                q_dict = {}
                for idx, q in enumerate(quantiles):
                    q_key = f"p{int(q*100)}"
                    q_dict[q_key] = [round(float(v), 2) for v in q_forecast[0, :horizon_days, idx]]

                return TimesFMOutput(
                    point_forecast=point_list,
                    quantiles=q_dict,
                    model_name=f"Google TimesFM ({self.checkpoint_path})",
                    is_mock=False
                )
            except Exception as exc:
                logger.error("Error durante la inferencia de TimesFM: %s. Usando fallback.", exc)

        # Fallback determinista
        return self._fallback_provider.forecast(history, horizon_days, quantiles)
