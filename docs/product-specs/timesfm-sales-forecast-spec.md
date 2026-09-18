# Especificación de Producto: Predicción de Ventas e Inventario PYME con Google TimesFM

- **Versión**: 1.0.0
- **Estado**: Aprobado
- **Dominio principal**: `src/domains/sales`
- **Proveedores**: `src/providers/timesfm`

---

## 1. Problema de Negocio

Las pequeñas y medianas empresas (tiendas minoristas físicas y comercios electrónicos en Shopify, WooCommerce o TPVs como Square/SumUp) carecen de herramientas accesibles de previsión de demanda. Esto genera:
1. **Roturas de stock imprevistas**: Pérdida directa de ventas y clientes descontentos.
2. **Exceso de inventario**: Capital inmovilizado y costes de almacenamiento innecesarios.
3. **Complejidad de modelos tradicionales**: Modelos como ARIMA o Prophet requieren ajuste manual de hiperparámetros y experiencia en ciencia de datos.

### La Solución: Google TimesFM (Zero-Shot)
Google TimesFM es un modelo fundacional pre-entrenado en más de 100.000 millones de puntos temporales reales. Permite realizar predicciones precisas de forma inmediata (*zero-shot*), sin necesidad de reentrenamiento, ofreciendo cuantiles probabilísticos para modelar la incertidumbre de la demanda.

---

## 2. Requerimientos Funcionales

### RF-1: Ingesta Flexible de Datos de Ventas
- Soporte para archivos CSV y Excel.
- Detección automática de dialectos y formatos comunes:
  - **Shopify export**: columnas `Created at`, `Lineitem name`, `Lineitem quantity`, `Total Sales`.
  - **TPV / Square / SumUp**: columnas `Date`, `Item`, `Qty`, `Gross Sales`.
  - **Formato Genérico**: mapeo inteligente por palabras clave (`fecha/date`, `producto/sku/item`, `ventas/cantidad/qty/sales`).
- Normalización automática: ordenación cronológica, imputación de días sin ventas con 0, y agregación por periodicidad diaria.

### RF-2: Pronóstico Multi-Horizonte con Cuantiles
- Horizontes de predicción configurables: **7 días** (operativo), **30 días** (táctico mensual), **60 días** (bimestral) y **90 días** (trimestral/temporada).
- Cálculo de cuantiles de incertidumbre:
  - **P10 (Conservador)**: Escenario de baja demanda (10% de probabilidad de vender menos).
  - **P50 (Mediana esperada)**: Demanda base más probable.
  - **P90 (Pico pesimista para stock)**: Escenario de alta demanda (90% de probabilidad de que la demanda no supere este nivel, ideal para aprovisionamiento seguro).

### RF-3: Motor Inteligente de Reposición y Rotura de Stock
- **Días de Inventario Restantes (DOI - Days of Inventory)**: Stock actual dividido entre el consumo diario promedio estimado en el horizonte P50.
- **Punto de Reorden (ROP - Reorder Point)**:
  $$ROP = (d_{P50} \times L) + SS$$
  Donde $L$ es el Lead Time (días de entrega del proveedor) y $SS$ es el stock de seguridad calculado con el cuantil P90 o factor Z ($SS = Z \times \sigma_L$).
- **Fecha Estimada de Rotura (Runout Date)**: Día exacto en el que el stock acumulado proyectado cae a cero.
- **Clasificación de Riesgo**:
  - `CRITICAL` (Rojo): Rotura proyectada en menos de $L$ días. Se requiere pedido urgente inmediato.
  - `WARNING` (Amarillo): Stock por debajo del ROP. Emitir orden de compra ordinaria.
  - `OPTIMAL` (Verde): Stock suficiente para cubrir el ciclo.
  - `OVERSTOCKED` (Azul): Stock superior al consumo estimado a 90 días.

### RF-4: API REST y Dashboard Visual
- Endpoints REST en FastAPI (`/api/upload`, `/api/forecast`, `/api/inventory/recommendations`, `/api/sample-data`).
- Dashboard web interactivo:
  - Selector de datasets de demostración (Gourmet Coffee Shop, Fashion Boutique) para prueba inmediata sin subir archivos.
  - Visualización gráfica de la serie histórica y el abanico de incertidumbre TimesFM (cono P10-P90).
  - Semáforos de riesgo y tabla exportable a CSV con lista de compra de reposición.

---

## 3. Requerimientos No Funcionales e Invariantes

1. **Arquitectura Harness**: Estricto cumplimiento de `types -> config -> repository -> service -> runtime -> ui`.
2. **Límite de Líneas**: Ningún archivo excederá 250 líneas de código.
3. **Resiliencia / Zero-Dependency Fallback**: El proveedor TimesFM debe arrancar y funcionar con su emulador local estadístico sin requerir tarjeta gráfica ni dependencias pesadas compiladas en Windows.
