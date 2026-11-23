# PSet 3 · Alerta temprana de volatilidad de AAPL

El proyecto estima al cierre de cada rueda si AAPL presentará alta volatilidad
durante las cinco ruedas siguientes. La clase positiva se define con el
percentil 80 de la volatilidad futura, estimado con el conjunto de entrenamiento.

## Datos y evaluación

La fuente es `PSET2_DB.OBT.AAPL_DAILY_OBT` en Snowflake. La extracción utilizada
contiene **4.087 filas**, con fecha de corte inclusive del **30 de septiembre
de 2026**.

Se usaron cinco pliegues de validación temporal con una separación de cinco
ruedas (`gap=5`). El conjunto de prueba contiene **805 fechas de alerta** a
partir del **11 de julio de 2023**. La métrica técnica fue ROC-AUC y la métrica
de negocio fue la diferencia de capital final frente a Buy & Hold.

## Configuración

Desde la raíz del repositorio, instala las dependencias en el Python que usarás
como kernel:

```powershell
python -m pip install -r requirements.txt
```

Si aún no tienes un `.env`, crea uno a partir de la plantilla:

```powershell
Copy-Item .env.example .env
```

Completa `.env` con tu cuenta, usuario, contraseña y rol de Snowflake. El rol
debe tener acceso de lectura a la OBT y permiso para usar el warehouse
configurado. Mantén `DATA_CUTOFF=2026-09-30` para reproducir la extracción de
la entrega. Git incluye `.env.example` como plantilla y excluye `.env`.

Con Docker Desktop activo, levanta MLflow:

```powershell
docker compose up -d mlflow
curl.exe -i --max-time 10 http://127.0.0.1:5000/health
```

Cuando el servidor responda `HTTP 200`, abre la
[interfaz local de MLflow](http://127.0.0.1:5000/). El servidor usa SQLite
para los metadatos y guarda los artefactos en un volumen persistente de Docker.
Para comprobar que puedes registrar una corrida y recuperar su artefacto,
ejecuta `python scripts/verificar_mlflow.py`.

## Orden de ejecución

| Notebook | Propósito |
|---|---|
| `notebooks/01_eda.ipynb` | Calidad de datos, análisis temporal y exploración del target. |
| `notebooks/02_features.ipynb` | Construcción de 18 features, prueba de fuga temporal y definición de la partición. |
| `notebooks/03_baseline_candidatos.ipynb` | Tres líneas base y cinco candidatos tabulares. |
| `notebooks/04_tuning.ipynb` | Ajuste de Random Forest, regresión logística y SVM con 30 configuraciones por modelo. |
| `notebooks/05_seleccion.ipynb` | Selección de finalistas, calibración del umbral en validación, evaluación en prueba y registro final. |
| `notebooks/06_verificacion_champion.ipynb` | Carga del modelo por alias y verificación del ROC-AUC registrado. |

Para reproducir el flujo en un servidor de MLflow nuevo, usa en `04_tuning`
los Run ID de candidatos que genere `03_baseline_candidatos`. Después, usa en
`05_seleccion` los Run ID padre que genere `04_tuning`. Las celdas de registro
crean nuevas corridas al ejecutarse. Para la entrega, usa **Restart → Run All**
y guarda los notebooks con las salidas visibles.

## Decisión final

La **regresión logística** fue elegida como `champion` y **Random Forest**
como `challenger`. En prueba, obtuvieron un ROC-AUC de **0,6439** y **0,6348**,
respectivamente. La logística también requirió menos tiempo de ajuste e
inferencia. El umbral elegido en validación dejó ambos modelos sin alertas
activas, por lo que las dos simulaciones igualaron el capital final de
Buy & Hold: **USD 18.126,50**.

El URI previsto para verificar el ganador es
`models:/alerta-volatilidad-aapl-modelo@champion`. La entrega se completa al
confirmar el alias, guardar la salida de verificación y exportar
`docs/corridas.csv`. Los resultados pueden revisarse en GitHub mediante las
salidas guardadas y el CSV. La reejecución desde cero requiere acceso a
Snowflake y un servidor local de MLflow.

La comparación incluyó cinco candidatos tabulares. La evaluación del modelo
fundacional Chronos y la prueba de prompting con un LLM quedaron pendientes.