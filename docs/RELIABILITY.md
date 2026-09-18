# Confiabilidad y SLOs (RELIABILITY.md)

Invariantes de confiabilidad del sistema de previsión e inventario:
- **Fallback Determinista**: Si el modelo pesado de Google TimesFM no está disponible (sin GPU, dependencias incompatibles o error de red), el sistema conmuta automáticamente y sin errores al proveedor estadístico local de alta fidelidad (`mock_provider.py`).
- **Manejo Determinista de Errores**: Todo error en parseo de CSVs/Excel o formatos desconocidos genera respuestas estructuradas HTTP 400 con diagnóstico claro de columnas faltantes.
- **Idempotencia en Predicciones**: Para una misma serie temporal histórica y semilla/horizonte, el pronóstico produce resultados consistentes y auditables.
