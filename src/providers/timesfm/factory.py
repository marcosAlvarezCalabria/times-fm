"""
Factoría de proveedores para Google TimesFM.
Gestiona la instanciación según las variables de entorno o parámetros de arranque.
"""

import os
from typing import Optional

from .interface import TimesFMProvider
from .mock_provider import LocalTimesFMMockProvider
from .google_provider import GoogleTimesFMProvider

_provider_instance: Optional[TimesFMProvider] = None


def get_timesfm_provider(force_mock: bool = False) -> TimesFMProvider:
    """
    Obtiene o crea una instancia del proveedor TimesFM.

    Args:
        force_mock: Si es True, fuerza el uso del emulador local sin intentar cargar pesos.

    Returns:
        Instancia de TimesFMProvider configurada.
    """
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    use_real = os.getenv("TIMESFM_USE_REAL", "false").lower() in ("true", "1", "yes")

    if force_mock or not use_real:
        _provider_instance = LocalTimesFMMockProvider()
    else:
        checkpoint = os.getenv("TIMESFM_CHECKPOINT", "google/timesfm-1.0-200m")
        _provider_instance = GoogleTimesFMProvider(checkpoint_path=checkpoint)

    return _provider_instance


def reset_timesfm_provider() -> None:
    """Permite reiniciar el proveedor (útil para tests)."""
    global _provider_instance
    _provider_instance = None
