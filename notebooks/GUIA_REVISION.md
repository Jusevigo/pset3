# Aplicar la revisión del PSet 3
Usa el entorno habitual y las mismas configuraciones de Snowflake y MLflow. Ejecuta cada notebook desde su carpeta o la raíz del repositorio.

1. **03:** activa `REGISTRAR_CANDIDATOS` una vez y ejecuta desde un kernel limpio. Calcula las líneas base, los candidatos y la ablación. El registro deja los IDs y la huella en `docs/revision_runs.json`. TimesFM se conserva como evidencia histórica y su recálculo es opcional. Claude usa las respuestas archivadas si coincide la huella.
2. **04:** activa `EJECUTAR_TUNING` y ejecuta desde un kernel limpio. Valida la procedencia y ajusta los tres mejores candidatos, con 30 configuraciones cada uno. Los nuevos IDs padre quedan en el mismo archivo JSON.
3. **05:** ejecuta primero con `EVALUAR_HOLDOUT = False` y `PUBLICAR_ALIAS = False` para revisar roles y umbrales fijados por validación. Para obtener las métricas de la reevaluación, activa `EVALUAR_HOLDOUT`. Activa `PUBLICAR_ALIAS` solamente al decidir promover esas versiones. El PSet 4 puede cargar el alias champion.
4. **06:** verifica los dos alias. Activa `EXPORTAR_CORRIDAS` para actualizar `docs/corridas.csv`. Si difiere la huella, la reproducción exacta queda pendiente hasta recuperar la extracción correspondiente o publicar modelos de la extracción actual.

Desactiva los indicadores de escritura después de guardar las salidas. Ejecutar 03 con el registro activo crea un nuevo conjunto de corridas y reinicia el archivo de IDs. Conserva las salidas de la ejecución completa para la revisión. El hold-out ya visto se trata como reevaluación retrospectiva.
