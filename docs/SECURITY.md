# Políticas de Seguridad (SECURITY.md)

1. **Validación de fronteras obligatoria (*Parse, don't validate*)**:
   - Todo archivo cargado por el usuario (CSV, Excel) pasa por validación de tamaño máximo, tipado y desinfección de cabeceras antes de ser procesado.
2. **Sin fuga de credenciales**:
   - Ninguna clave API de Google Cloud o Vertex AI se almacena en el código fuente; se utilizan variables de entorno validadas en `src/domains/sales/config/`.
3. **Privacidad de datos de ventas**:
   - Los datos históricos de clientes y ventas de la tienda se procesan localmente o en el backend autorizado sin telemetría de datos sensibles no anonimizados.
