# Guía del Repositorio para Agentes

> **Regla de Oro**: Este repositorio es 100% generado y mantenido por agentes. Las personas dirigen; los agentes ejecutan.
> Ningún código se escribe a mano. Mantén las invariantes, respeta la arquitectura y valida siempre antes de proponer cambios.

---

## 1. Mapa del Sistema de Registro (Divulgación Progresiva)

No intentes cargar todo el contexto a la vez. Consulta los documentos específicos según tu tarea:

- **Arquitectura y Capas**: Consulta [`ARCHITECTURE.md`](file:///./ARCHITECTURE.md) antes de crear o mover archivos.
- **Creencias Fundamentales**: Consulta [`docs/design-docs/core-beliefs.md`](file:///./docs/design-docs/core-beliefs.md).
- **Especificaciones de Producto**: Consulta [`docs/product-specs/`](file:///./docs/product-specs/).
- **Puntuación de Calidad y Deuda**: Consulta [`docs/QUALITY_SCORE.md`](file:///./docs/QUALITY_SCORE.md).
- **Planes de Ejecución (Tareas complejas)**: Consulta [`docs/PLANS.md`](file:///./docs/PLANS.md) y [`docs/exec-plans/`](file:///./docs/exec-plans/).

---

## 2. Invariantes de Arquitectura y Código

1. **Dependencias estrictas hacia adelante**: Dentro de cada dominio, las capas solo pueden importar en esta dirección:
   `Tipos` → `Config` → `Repositorio` → `Servicio` → `Runtime` → `UI`
2. **Inquietudes Transversales**: Telemetría, Auth, Feature Flags y conectores externos SOLO entran a través de `Providers`.
3. **Parse, don't validate**: Toda entrada externa (HTTP, env vars, DB, eventos) debe validarse estrictamente con esquemas tipados en los límites.
4. **Logs Estructurados**: Prohibido el uso de logging plano sin contexto; usa siempre el logger estructurado con campos de contexto.
5. **Tamaño de Archivos**: Mantén los archivos por debajo de 250 líneas. Divide si crecen demasiado.

---

## 3. Protocolo de Trabajo del Agente

Para cada tarea asignada:

1. **Crear o activar plan**: Para tareas no triviales, crea un plan de ejecución en `docs/exec-plans/active/<tarea>.md`.
2. **Trabajar en aislamiento**: Cada tarea debe desarrollarse en su propio `git worktree` o rama efímera.
3. **Validación mecánica antes de proponer cambios**:
   - Ejecuta linter estructural: `python scripts/lint_layers.py` (o comando equivalente).
   - Ejecuta suite de tests: `npm test` / `pytest` / `go test`.
   - Si la tarea modifica UI, verifica visualmente mediante DevTools / snapshots.
4. **Auto-remediación**: Si un linter o test falla, lee el mensaje de error remedial, corrige la causa raíz y vuelve a validar.
5. **Cierre**: Mueve el plan completado a `docs/exec-plans/completed/<tarea>.md` y abre la Pull Request con evidencia clara.
