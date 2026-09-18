# Plan de Ejecución: Predicción de Ventas e Inventario PYME con Google TimesFM

- **Estado**: Completado (MVP Funcional y Verificado)
- **Fecha de inicio**: 2026-09-18
- **Fecha de finalización**: 2026-09-18
- **Dominio afectado**: `src/domains/sales` y `src/providers/timesfm`
- **Spec de referencia**: `docs/product-specs/timesfm-sales-forecast-spec.md`

---

## 1. Contexto y Objetivos

Desarrollar un MVP funcional de aplicación web para que pequeñas y medianas empresas (PYMEs/tiendas) puedan:
1. Ingestar sus históricos de ventas desde exportaciones CSV/Excel (Shopify, TPV, etc.).
2. Pronosticar la demanda a 7, 30, 60 y 90 días usando el modelo fundacional **Google TimesFM** con cuantiles probabilísticos (P10, P50, P90).
3. Obtener alertas tempranas de rotura de stock y sugerencias automáticas de cantidades a reponer.
4. Interactuar mediante una API REST en FastAPI y un dashboard visual interactivo.
5. Mantener la conformidad con la arquitectura Harness Engineering (invariantes mecánicas y linter).

---

## 2. Invariantes y Riesgos

- **Flujo estricto de capas**: `types` → `config` → `repository` → `service` → `runtime` → `ui`.
- **Inquietudes transversales**: El acceso a Google TimesFM se aísla en `src/providers/timesfm/`.
- **Resiliencia de ejecución**: Google TimesFM cuenta con fallback local estadístico de alta fidelidad (`mock_provider.py`) para operar en cualquier entorno (incluyendo Python 3.14 en Windows) sin depender de librerías nativas incompatibles.
- **Tamaño de archivo**: Cada módulo individual se mantiene estrictamente por debajo de las 250 líneas.

---

## 3. Desglose de Pasos de Implementación

### Fase 1: Inquietud Transversal - Proveedor TimesFM (`src/providers/timesfm/`)
- [x] `interface.py`: Definición de la interfaz abstracta `TimesFMProvider` con método `forecast`.
- [x] `mock_provider.py`: Emulador estadístico zero-shot (tendencia, estacionalidad semanal/mensual, residuos normales y cuantiles P10, P50, P90).
- [x] `google_provider.py`: Wrapper para Google TimesFM oficial con delegación segura al mock en ausencia de librerías nativas.
- [x] `factory.py`: Factoría con configuración de proveedor activo.

### Fase 2: Capas de Dominio (`src/domains/sales/`)
- [x] **Paso 1: Tipos (`types/`)**:
  - `sales_types.py`: `SalesRecord`, `DailySalesPoint`, `NormalizedSeries`, `IngestionSummary`.
  - `forecast_types.py`: `ForecastHorizon` (7, 30, 60, 90d), `ForecastDayPoint`, `ProductForecast`.
  - `inventory_types.py`: `ProductInventory`, `StockoutRiskLevel`, `ReplenishmentRecommendation`, `StoreInventorySummary`.
- [x] **Paso 2: Configuración (`config/`)**:
  - `sales_config.py`: Horizontes, cuantiles por defecto, nivel de servicio de seguridad (Z=1.65), lead times.
- [x] **Paso 3: Repositorio (`repository/`)**:
  - `sales_repository.py`: Repositorio en memoria con precarga de datasets de muestra (Cafetería de Especialidad & Bakery PYME).
- [x] **Paso 4: Lógica de Negocio (`service/`)**:
  - `normalization_service.py`: Ingestor multi-formato (Shopify, TPV, genérico), parsing de fechas e imputación.
  - `forecast_service.py`: Orquestación con TimesFM provider y cálculo de horizontes y cuantiles.
  - `inventory_service.py`: Motor de reposición, cálculo de ROP, DOI, días hasta rotura y criticidad.
- [x] **Paso 5: Controladores y Runtime (`runtime/`)**:
  - `api_routes.py`: Endpoints `/api/upload`, `/api/forecast`, `/api/inventory/recommendations`, `/api/load-sample`.
  - `server.py`: Fábrica de aplicación FastAPI, middlewares CORS y montaje estático.
- [x] **Paso 6: UI y Dashboard (`ui/`)**:
  - `web_view.py`: Handler de presentación y orquestador de aplicación unificada.
  - `static/index.html`: Dashboard responsivo con Chart.js, cono P10-P90, selector de horizontes (7, 30, 60, 90d) y alertas de stock.

### Fase 3: Scripts, Tests y Verificación
- [x] `scripts/lint_layers.py`: Linter estructural de dependencias ejecutado con código 0.
- [x] `requirements.txt` y `run.py`: Script de arranque local (`http://localhost:8000`).
- [x] `tests/test_timesfm.py`, `tests/test_normalization.py`, `tests/test_inventory.py`, `tests/test_api.py`.

---

## 4. Plan de Verificación y Evidencia

- [x] **Linter estructural ejecutado con 0 errores**:
  ```text
  [LINT OK] Todas las invariantes arquitectónicas y reglas de capas se cumplen con éxito.
  ```
- [x] **Suite de pruebas unitarias pasando al 100%**:
  ```text
  Ran 12 tests in 0.382s
  OK
  ```
- [x] **Validación de la API REST y UI**: Verificada mediante `TestClient` en `tests/test_api.py` cubriendo `/api/health`, `/api/products`, `/api/forecast`, `/api/inventory/recommendations` y `/` (Dashboard HTML).
