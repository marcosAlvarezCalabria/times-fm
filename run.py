#!/usr/bin/env python3
"""
Punto de entrada para ejecutar el servidor local del MVP de Google TimesFM.
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import uvicorn
from src.domains.sales.ui import get_full_application

app = get_full_application()

if __name__ == "__main__":
    port = 8000
    print("=================================================================")
    print(f"[OK] Iniciando TimesFM Sales Forecast MVP en: http://localhost:{port}")
    print("[OK] Dashboard interactivo listo para PYMEs y retail")
    print("=================================================================")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
