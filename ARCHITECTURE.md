# Arquitectura del Sistema e Invariantes de Capas

Este documento define la estructura de dominios empresariales y las reglas estrictas de dependencia unidireccional que gobiernan este repositorio.

```
       ┌─────────────────────────────────────────────────────────────┐
       │             INQUIETUDES TRANSVERSALES (PROVIDERS)           │
       │     Google TimesFM • Telemetría • Auth • Mock Provider      │
       └──────────────────────────────┬──────────────────────────────┘
                                      │ Inyección explícita
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DOMINIO EMPRESARIAL: SALES                       │
│                                                                         │
│  [1. Tipos / Schemas]  (sales_types, forecast_types, inventory_types)   │
│          │                                                              │
│          ▼                                                              │
│  [2. Config]           (sales_config: horizontes, cuantiles, lead times)│
│          │                                                              │
│          ▼                                                              │
│  [3. Repositorio]      (sales_repository: series históricas, catálogos) │
│          │                                                              │
│          ▼                                                              │
│  [4. Servicio]         (normalization, forecast_service, inventory)     │
│          │                                                              │
│          ▼                                                              │
│  [5. Runtime]          (FastAPI routes, controllers, app server)        │
│          │                                                              │
│          ▼                                                              │
│  [6. UI]               (Dashboard web interactivo, Chart.js, HTML/JS)   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Definición de Capas y Dependencias Permitidas

Dentro del dominio `sales` (`src/domains/sales/<capa>/`), las dependencias están estrictamente limitadas a avanzar en orden hacia adelante:

| Capa | Responsabilidad | ¿De quién puede importar? | ¿Quién puede importarlo? |
| :--- | :--- | :--- | :--- |
| **`types/`** | Interfaces puras, DTOs y esquemas de validación de frontera. | Nada interno del dominio. Solo librerías estándar o de esquemas. | Config, Repositorio, Servicio, Runtime, UI. |
| **`config/`** | Parámetros del dominio y configuración tipada. | `types/`. | Repositorio, Servicio, Runtime, UI. |
| **`repository/`** | Queries, llamadas a base de datos, persistencia de series. | `types/`, `config/`, Providers (DB). | Servicio. |
| **`service/`** | Lógica de negocio (forecast, reposición, normalización). | `types/`, `config/`, `repository/`, Providers. | Runtime. |
| **`runtime/`** | Handlers de endpoints HTTP (FastAPI), eventos. | `types/`, `config/`, `service/`. | UI (o servidor principal). |
| **`ui/`** | Componentes de presentación, vistas o dashboard cliente. | `types/`, `config/`, `runtime/` (APIs). | Ninguno dentro del backend. |

> [!CAUTION]
> **Prohibido el acoplamiento inverso o circular**:
> - Un `repository` **NUNCA** puede importar de `service` ni de `runtime`.
> - Un `service` **NUNCA** puede importar de `runtime` ni de `ui`.
> - Violaciones de esta regla romperán el linter de CI (`scripts/lint_layers.py`).

---

## 2. Inquietudes Transversales (`src/providers/`)

Las utilidades compartidas y servicios externos no deben ser importados arbitrariamente en cualquier archivo:
- **Google TimesFM / Previsión**: Se consume a través del proveedor transversal (`src/providers/timesfm`).
- **Telemetría y Logs**: Se consumen a través del proveedor de observabilidad (`src/providers/telemetry`).
- **Autenticación**: Proveedor de contexto de identidad (`src/providers/auth`).

---

## 3. Principio *Parse, Don't Validate*

- Todas las fronteras del sistema (entradas HTTP, archivos CSV/Excel de Shopify o TPVs, configuraciones) deben ser **parseadas y transformadas** a tipos validados en el momento de recepción.
- No se permiten tipos no validados o diccionarios genéricos en capas internas de `service` o `repository`.
