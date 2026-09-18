"""
Proveedor transversal para Google TimesFM y emulador estadístico local.
"""

from .interface import TimesFMOutput, TimesFMProvider
from .mock_provider import LocalTimesFMMockProvider
from .google_provider import GoogleTimesFMProvider
from .factory import get_timesfm_provider, reset_timesfm_provider

__all__ = [
    "TimesFMOutput",
    "TimesFMProvider",
    "LocalTimesFMMockProvider",
    "GoogleTimesFMProvider",
    "get_timesfm_provider",
    "reset_timesfm_provider",
]
