# Matriz de Calidad y Deuda Técnica (Quality Score)

Este documento califica el estado de cada dominio empresarial e infraestructura del repositorio. Es actualizado periódicamente por agentes de mantenimiento y recolección de basura (*anti-entropía*).

---

## 1. Escala de Calidad

- **Nivel A**: Cobertura > 90%, cumplimiento estricto de capas, logs estructurados al 100%, specs y docs actualizados.
- **Nivel B**: Cobertura 75%-90%, sin violaciones de capas, logs estructurados, documentación parcial.
- **Nivel C**: Deuda técnica acumulada, falta de tests en capas clave o specs desactualizadas. Requiere micro-PRs de remediación.
- **Nivel D / F**: Violación de invariantes o capas. Bloquea nuevas features en ese dominio hasta que se subsane.

---

## 2. Puntuación Actual por Dominio

| Dominio | Calificación | Cobertura Tests | Conformidad Capas | Estado de Documentación | Última Revisión |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `src/domains/sales` | **A** | 100% (12/12 tests OK) | 100% (0 violaciones) | Actualizada (`timesfm-sales-forecast-spec.md`) | 2026-09-18 |
| `src/providers/timesfm` | **A** | 100% (Cuantiles + Fallback) | 100% | Actualizada | 2026-09-18 |

---

## 3. Registro de Acciones de Remediación Pendientes

- [x] Implementar la suite de tests unitarios e integración para `service/forecast_service.py` e `inventory_service.py`.
- [x] Ejecutar `python scripts/lint_layers.py` para asegurar 0 violaciones.
- [x] Validar que todos los archivos cumplan con el límite de 250 líneas.
