# PSet 3 · Alerta temprana de volatilidad de AAPL

El proyecto estima al cierre de cada rueda si la volatilidad de AAPL será alta
durante las próximas cinco ruedas. La clase positiva se define mediante el P80
de la volatilidad futura, estimado únicamente con el entrenamiento.

## Datos y evaluación

- **Fuente:** `PSET2_DB.OBT.AAPL_DAILY_OBT` en Snowflake, con corte inclusive al
  `2026-09-30`. La extracción utilizada contiene 4.087 filas.
- **Validación:** cinco pliegues temporales con `gap=5` y un hold-out de 805
  fechas a partir del `2023-07-11`.
- **Métricas:** ROC-AUC para comparar modelos y diferencia de capital final
  frente a Buy & Hold para evaluar las alertas.

## Reproducir el experimento

1. Desde la raíz del repositorio, instala las dependencias en el Python que
   usarás como kernel y crea tu archivo de configuración local:

   ```powershell
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

   Completa `.env` con credenciales propias y un rol autorizado para consultar
   la OBT y usar el warehouse. Si ya tienes un `.env`, reutilízalo. Las
   credenciales se mantienen fuera de Git.

2. Con Docker Desktop activo, inicia el servidor local de MLflow:

   ```powershell
   docker compose up -d mlflow
   curl.exe -i --max-time 10 http://127.0.0.1:5000/health
   ```

   Cuando `/health` devuelva `200 OK`, abre [MLflow](http://127.0.0.1:5000).
   El servidor usa SQLite para los metadatos y un volumen Docker persistente
   para conservar los datos y artefactos. Para comprobar el registro de una
   corrida y su artefacto, ejecuta `python scripts/verificar_mlflow.py`.

3. Ejecuta los notebooks en este orden:

   | Notebook | Contenido |
   |---|---|
   | `01_eda.ipynb` | Calidad de la OBT y análisis exploratorio. |
   | `02_features.ipynb` | Construcción de features, pruebas de alineación temporal y definición de los pliegues. |
   | `03_baseline_candidatos.ipynb` | Líneas base y comparación de cinco candidatos tabulares. |
   | `04_tuning.ipynb` | 30 configuraciones por cada uno de los tres candidatos seleccionados. |
   | `05_seleccion.ipynb` | Elección del umbral en validación y evaluación de los dos finalistas en prueba. |

   En `04_tuning.ipynb`, usa los Run ID de los candidatos de tu servidor.
   En `05_seleccion.ipynb`, usa los Run ID padre que genere el tuning.
   Ejecutar las celdas de registro vuelve a crear corridas.

## Resultado y estado

La regresión logística fue seleccionada como `champion` propuesto por su
ROC-AUC en prueba (**0,6439** frente a **0,6348** de Random Forest), su menor
tiempo de ajuste e inferencia y su explicabilidad. En validación, ambos
finalistas eligieron el umbral `1,01`, que mantiene la exposición en 100 %.
En el hold-out, ambas políticas igualaron el capital final de Buy & Hold
(**USD 18.126,50**).

Las salidas guardadas en los notebooks permiten revisar los resultados desde
GitHub. Quedan pendientes la asignación de `champion` y `challenger` en el
Model Registry, la verificación en un notebook limpio y la exportación final
a `docs/corridas.csv`. La evaluación de Chronos quedó incompleta por un bloqueo
del entorno local y la prueba de prompting con un LLM quedó pendiente.