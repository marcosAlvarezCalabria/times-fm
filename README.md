# TimesFM Sales Forecast & Inventory AI for SMEs

Sistema de pronóstico de demanda y optimización de inventario para pequeñas y medianas empresas (PYMEs, comercio electrónico Shopify y tiendas físicas/TPV) utilizando el modelo fundacional **Google TimesFM** (zero-shot time-series foundation model).

Arquitectura construida bajo los principios de **Harness Engineering (Agent-First)**.

---

## 🚀 Características Principales

1. **Google TimesFM Zero-Shot Forecasting**:
   - Predicción probabilística sin necesidad de entrenamiento local o ajuste manual.
   - Cuantiles de incertidumbre: **P10** (escenario conservador), **P50** (mediana más probable), **P90** (escenario de alta demanda para protección de stock).
   - Horizontes de pronóstico flexibles: 7, 30, 60 y 90 días.
   - Fallback estadístico local de alta fidelidad (`mock_provider.py`) para desarrollo sin requisitos de GPU.

2. **Ingesta Multi-Formato**:
   - Detección y normalización automática de exportaciones de **Shopify**, **Square/SumUp** y CSV/Excel genéricos.
   - Imputación de días sin ventas y agregación diaria homogénea.

3. **Motor Inteligente de Reposición y Rotura de Stock**:
   - Cálculo automático de **Punto de Reorden (ROP)** y **Stock de Seguridad (SS)**.
   - Estimación de **Días de Inventario Restantes (DOI)** y **Fecha Prevista de Rotura (Runout Date)**.
   - Semáforo de urgencia (`CRITICAL`, `WARNING`, `OPTIMAL`, `OVERSTOCKED`) con cantidades exactas a pedir y cálculo de presupuesto de compra.

4. **Dashboard Visual Interactivo**:
   - Gráfico de cono de incertidumbre (P10-P90) con Chart.js.
   - Carga con 1-clic de datos de muestra para pruebas inmediatas.
   - Alertas de inventario y tabla de reposición exportable a CSV.

---

## 🏛️ Estructura del Proyecto (Harness Engineering)

```
times-fm/
├── AGENTS.md                               # Directrices del repositorio para agentes
├── ARCHITECTURE.md                         # Invariantes y reglas de capas unidireccionales
├── CLAUDE.md                               # Entrypoint para Claude
├── docs/                                   # Sistema de Registro
│   ├── design-docs/core-beliefs.md         # Filosofía operativa
│   ├── exec-plans/                         # Planes de ejecución activos y completados
│   │   ├── active/timesfm-sales-forecast.md
│   │   └── TEMPLATE.md
│   ├── product-specs/                      # Especificaciones de producto
│   │   └── timesfm-sales-forecast-spec.md
│   ├── PLANS.md
│   ├── QUALITY_SCORE.md
│   ├── RELIABILITY.md
│   └── SECURITY.md
├── scripts/
│   └── lint_layers.py                      # Linter estructural de capas e invariantes
├── src/
│   ├── domains/sales/                      # Dominio de Ventas y Previsión
│   │   ├── types/                          # DTOs y validación de frontera
│   │   ├── config/                         # Parámetros y horizontes
│   │   ├── repository/                     # Acceso y persistencia de series
│   │   ├── service/                        # Lógica de forecast y reposición
│   │   ├── runtime/                        # Controladores HTTP y FastAPI
│   │   └── ui/                             # Dashboard web interactivo
│   └── providers/                          # Inquietudes transversales
│       └── timesfm/                        # Google TimesFM Provider & Mock
└── tests/                                  # Pruebas unitarias y de integración
```

---

## 📋 Reglas de Capas y Validación

Las dependencias avanzan en una única dirección:
$$\text{types} \longrightarrow \text{config} \longrightarrow \text{repository} \longrightarrow \text{service} \longrightarrow \text{runtime} \longrightarrow \text{ui}$$

Para validar mecánicamente la arquitectura en cualquier momento:
```bash
python scripts/lint_layers.py
```
