# PSet 3 · Alerta temprana de volatilidad de AAPL

El proyecto estima, al cierre de cada rueda bursátil, si AAPL presentará alta volatilidad durante las cinco ruedas siguientes. La unidad de predicción es acción–fecha. La clase positiva se define con el percentil 80 de la volatilidad futura, calculado con el conjunto de entrenamiento.

## Datos y validación

La fuente es `PSET2_DB.OBT.AAPL_DAILY_OBT` en Snowflake. La extracción de referencia contiene 4.087 filas, con fecha de corte del 30 de septiembre de 2026.

La comparación usa cinco pliegues temporales con `gap=5`. La separación permite que la última etiqueta de entrenamiento, que depende de los cinco retornos siguientes, se complete antes de comenzar la validación. El hold-out contiene 805 fechas de predicción a partir del 11 de julio de 2023. En esta revisión se reutilizó ese período para reevaluar los modelos.

## Configuración local

Desde la raíz del repositorio, instala las dependencias en el entorno que usarás como kernel de Jupyter:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si ya tienes un `.env`, conserva ese archivo. Configura la conexión a Snowflake con un rol que pueda leer la OBT y usar el warehouse correspondiente. Mantén `DATA_CUTOFF=2026-09-30` para reproducir la extracción. Las credenciales se guardan únicamente en el `.env` local.

Con Docker Desktop activo, inicia MLflow:

```powershell
docker compose up -d mlflow
curl.exe --max-time 5 http://127.0.0.1:5000/health
```

La interfaz local está en [MLflow](http://127.0.0.1:5000).

## Orden de ejecución

| Notebook | Propósito |
|---|---|
| `01_eda.ipynb` | Revisar la calidad de la OBT y explorar los retornos y el target. |
| `02_features.ipynb` | Construir las variables y comprobar su disponibilidad al momento de la predicción. |
| `03_baseline_candidatos.ipynb` | Evaluar líneas base y candidatos. Documentar la ablación, TimesFM y el piloto con Claude. |
| `04_tuning.ipynb` | Ajustar los tres mejores candidatos con 30 configuraciones por modelo. |
| `05_seleccion.ipynb` | Fijar los roles y los umbrales en validación, reevaluar el hold-out y publicar las versiones en MLflow. |
| `06_verificacion_champion.ipynb` | Cargar ambos modelos por alias, reproducir las métricas y exportar las corridas. |

Para reproducir el flujo con nuevas corridas, activa `REGISTRAR_CANDIDATOS` en `03` y luego `EJECUTAR_TUNING` en `04`. Los notebooks comparten `docs/revision_runs.json` para enlazar los IDs y comprobar la huella del conjunto de desarrollo. En `05`, `EVALUAR_HOLDOUT` habilita la evaluación y `PUBLICAR_ALIAS` actualiza los alias del registro. Activa la publicación únicamente cuando quieras cambiar las versiones que consumen los proyectos dependientes.

## Resultados y Model Registry

Se eligió Random Forest como `champion` por su ROC-AUC medio de validación cruzada, antes de reevaluar el hold-out. La regresión logística quedó como `challenger`.

| Alias | Modelo | Versión | ROC-AUC en validación | ROC-AUC en hold-out |
|---|---|---:|---:|---:|
| `champion` | Random Forest | 3 | 0,7226 | 0,635553 |
| `challenger` | Regresión logística | 4 | 0,7099 | 0,643915 |

El PSet 4 carga el ganador mediante `models:/alerta-volatilidad-aapl-modelo@champion`. El **umbral de alerta del champion es 0,90**. El **P80 final de 2,1072 %** se usa para construir la etiqueta observada de volatilidad alta.

En el hold-out, Random Forest emitió cero alertas e igualó a Buy & Hold. La regresión logística emitió siete alertas y redujo el máximo drawdown de 33,36 % a 32,49 %, con un capital final USD 565,60 inferior al de Buy & Hold.

Las métricas de ambos alias se reprodujeron en `06_verificacion_champion.ipynb`. El archivo `docs/corridas.csv` contiene 212 corridas exportadas mediante `mlflow.search_runs`, incluidas las 90 configuraciones del tuning revisado.