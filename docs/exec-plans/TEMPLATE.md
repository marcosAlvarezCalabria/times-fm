# Plan de Ejecución: [Título de la Tarea]

- **Estado**: En progreso <!-- En progreso | Completado | Descartado -->
- **Fecha de inicio**: YYYY-MM-DD
- **Dominio afectado**: `src/domains/[dominio]`
- **Spec de referencia**: `docs/product-specs/[spec].md`

---

## 1. Contexto y Objetivos
Describe el problema a resolver y los criterios de aceptación exactos que deben cumplirse.

## 2. Invariantes y Riesgos
- ¿Qué capas se modifican o añaden?
- ¿Existen riesgos de regresión o cambios de esquema?

## 3. Desglose de Pasos de Implementación

- [ ] **Paso 1: Tipos y Esquemas**: Definir o actualizar modelos en `src/domains/[dominio]/types/`.
- [ ] **Paso 2: Configuración**: Definir parámetros en `src/domains/[dominio]/config/`.
- [ ] **Paso 3: Persistencia**: Implementar almacenamiento en `src/domains/[dominio]/repository/`.
- [ ] **Paso 4: Lógica de Negocio**: Implementar servicio en `src/domains/[dominio]/service/`.
- [ ] **Paso 5: Endpoints / Runtime**: Conectar handlers en `src/domains/[dominio]/runtime/`.
- [ ] **Paso 6: UI (si aplica)**: Crear componentes en `src/domains/[dominio]/ui/`.

## 4. Plan de Verificación y Evidencia
- [ ] Linter estructural ejecutado con 0 errores: `python scripts/lint_layers.py`
- [ ] Tests unitarios y de integración pasando: `pytest`
- [ ] Verificación visual o métrica.

## 5. Notas de Cierre y Decisiones Tomadas
Registra cualquier decisión arquitectónica relevante tomada durante la ejecución antes de mover este archivo a `docs/exec-plans/completed/`.
