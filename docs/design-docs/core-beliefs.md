# Creencias Fundamentales y Filosofía del Repositorio

Este documento define los principios no negociables que gobiernan las decisiones técnicas de los agentes y revisores en este proyecto.

---

## 1. Cero Código Manual (Las Personas Dirigen, los Agentes Ejecutan)
- Cada línea de código, test, script de CI y documentación en este repositorio es generada por agentes.
- Los humanos definen la intención, los criterios de aceptación y evalúan los resultados.
- Si un agente comete un error, no se corrige a mano: se mejora la especificación, el linter o la herramienta que faltaba para que el agente pueda resolverlo de forma autónoma.

## 2. Abstracciones Aburridas y Predecibles
- Preferimos librerías probadas, estables y bien representadas en el conocimiento de los LLMs.
- Preferimos módulos propios bien tipados y testeados al 100% antes que introducir dependencias externas opacas o mágicas.

## 3. Restricciones Mecánicas antes que Guías Pasivas
- Si una regla no se puede validar mediante un script, linter o test automático, la regla decaerá con el tiempo.
- Toda restricción de estilo, tamaño de archivo (< 250 líneas) o arquitectura debe estar respaldada por una verificación mecánica.

## 4. Los Planes son Artefactos de Primer Nivel
- El trabajo complejo no se improvisa: se documenta en un plan de ejecución en `docs/exec-plans/active/`.
- El progreso se registra a medida que se avanza y se archiva en `docs/exec-plans/completed/` como memoria histórica del proyecto.

## 5. Rendimiento y Desbloqueo Rápido
- Corregir código generado por agentes es económico; retrasar una PR indefinidamente por nimiedades es costoso.
- Las PRs son pequeñas, enfocadas y se validan con linters y pruebas antes de integrarse.
