# Sistema de alerta temprana de volatilidad para acciones

**PSet 3 · Experimentación y selección de modelos**

El proyecto predice si AAPL presentará alta volatilidad durante las próximas
cinco ruedas bursátiles. Se genera una predicción después del cierre de cada
rueda con la información disponible hasta ese momento. La unidad de análisis
es una acción por fecha de negociación.

La clasificación se evaluará también mediante una simulación de negocio.
Ante una alerta, la estrategia reduce la exposición a AAPL del 100 % al 75 %
durante cinco ruedas y se compara con Buy & Hold.

## Estado del proyecto

El avance incluye la lectura de la OBT desde Snowflake, el análisis exploratorio,
la construcción de 18 características, la partición cronológica, la validación
cruzada temporal y el preprocesamiento reutilizable en scikit-learn. También se
verificó que el servidor local de MLflow guarda los parámetros de una corrida
y permite recuperar sus artefactos.

El entrenamiento de las líneas base y los candidatos, el ajuste de
hiperparámetros y la evaluación final corresponden a las siguientes etapas.
La corrida `verificacion_tracking` corresponde a la comprobación del servidor.

## Fuente de datos

| Elemento | Valor |
|---|---|
| Origen del notebook | `PSET2_DB.OBT.AAPL_DAILY_OBT` en Snowflake |
| Activo | AAPL |
| Fecha de corte de extracción | `2026-09-30`, inclusive |
| Rango de la extracción verificada | `2010-07-01` a `2026-09-30` |
| Dimensiones de la OBT extraída | 4.087 filas × 19 columnas |
| Precio utilizado para los rendimientos | `ADJ_CLOSE_PRICE` |

Los notebooks consultan Snowflake mediante `cargar_obt()` de `src/datos.py`.
El archivo `scripts/export_snapshot.py` permite guardar una copia local en CSV
para inspección y calcular el SHA-256 del archivo exportado. La ejecución de
los notebooks usa la consulta a Snowflake.

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `notebooks/01_eda.ipynb` | Calidad de la OBT, estadística descriptiva, estructura temporal, distribución del target, valores atípicos, correlaciones y desbalance de clases. |
| `notebooks/02_features.ipynb` | Construcción de características, preparación del dataset, partición temporal y verificación del preprocesamiento. |
| `notebooks/03_baseline_candidatos.ipynb` | Configuración de MLflow para las corridas de línea base y modelos candidatos. |
| `src/datos.py` | Conexión a Snowflake y carga de la OBT con fecha de corte. |
| `src/pipeline.py` | Preprocesamiento con `ColumnTransformer` y construcción del `Pipeline` de scikit-learn. |
| `scripts/export_snapshot.py` | Exportación opcional de la OBT a un CSV local. |
| `scripts/verificar_mlflow.py` | Prueba reproducible del registro de una corrida y su artefacto. |
| `docker-compose.yml` | Servidor local de MLflow y volumen persistente. |
| `requirements.txt` | Dependencias de Python. |
| `.env.example` | Plantilla para configurar la conexión a Snowflake. |

## Reproducción local

Los siguientes comandos están escritos para PowerShell. Ejecútalos desde la
raíz del repositorio con Python 3.10 y Docker Desktop disponibles.

### 1. Preparar el entorno de Python

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ipykernel install --user --name pset3 --display-name "Python (PSet 3)"
```

Selecciona el kernel **Python (PSet 3)** al abrir los notebooks en VS Code o Jupyter.

### 2. Configurar Snowflake

Copia la plantilla y completa `.env` con tus propias credenciales:

```powershell
Copy-Item .env.example .env
```

| Variable | Valor o descripción |
|---|---|
| `SNOWFLAKE_ACCOUNT` | Identificador de la cuenta de Snowflake. |
| `SNOWFLAKE_USER` | Usuario con acceso a la OBT. |
| `SNOWFLAKE_PASSWORD` | Contraseña del usuario. |
| `SNOWFLAKE_ROLE` | Rol con permisos para consultar la OBT. En el entorno del proyecto se usó `PSET2_ROLE`. |
| `SNOWFLAKE_WAREHOUSE` | Warehouse autorizado para ejecutar la consulta. En el proyecto se usó `COMPUTE_WH`. |
| `DATA_CUTOFF` | `2026-09-30`. Fecha máxima incluida por `cargar_obt()`. |

El script opcional `export_snapshot.py` usa además `SNOWFLAKE_DATABASE=PSET2_DB`
y `SNOWFLAKE_SCHEMA=OBT`. Mantén `.env` fuera del control de versiones.

Para comprobar la lectura antes de abrir los notebooks:

```powershell
.\.venv\Scripts\python.exe -c "from src.datos import cargar_obt; print(cargar_obt().shape)"
```

Para la extracción verificada, la salida esperada es `(4087, 19)`.

### 3. Levantar y verificar MLflow

```powershell
docker compose config --quiet
docker compose up -d mlflow
docker compose ps mlflow
curl.exe -i --max-time 10 http://127.0.0.1:5000/health
```

Cuando `/health` devuelva `HTTP 200`, abre la
[interfaz local de MLflow](http://127.0.0.1:5000/) y ejecuta:

```powershell
.\.venv\Scripts\python.exe scripts\verificar_mlflow.py
```

El script imprime el ID de la corrida `verificacion_tracking` en el experimento
**Sistema de alerta temprana de volatilidad para acciones**. En la corrida
deben aparecer el parámetro `prueba = conexion_local` y el artefacto
`verificacion.txt`.

El servidor usa SQLite como backend para los metadatos y un directorio local
como almacén de artefactos. Ambos se conservan en el volumen de Docker
`mlflow_data`. El notebook y la imagen del servidor usan MLflow 3.10.0.

### 4. Ejecutar los notebooks en orden

1. **`01_eda.ipynb`** carga la OBT y examina la calidad de los datos, los
   rendimientos diarios y la distribución de la volatilidad futura.
2. **`02_features.ipynb`** construye las 18 características, alinea la
   volatilidad futura por fecha y verifica el corte del hold-out, los pliegues
   temporales y el preprocesamiento.
3. **`03_baseline_candidatos.ipynb`** se conecta al experimento de MLflow.
   En el estado actual, este notebook contiene la configuración de tracking.
   Las corridas de modelado se incorporarán en la siguiente etapa.

Para revisar el avance desde GitHub, se pueden consultar las salidas guardadas
en los notebooks. Para volver a ejecutarlos desde cero se requiere acceso de
lectura a la OBT en Snowflake con una cuenta autorizada.

## Preparación y diseño de validación

La volatilidad futura en la fecha \(t\) se define como la desviación estándar
de los cinco rendimientos diarios de \(t+1\) a \(t+5\). La clase positiva
corresponde a una volatilidad superior al **percentil 80 estimado con los datos
de entrenamiento**. El P80 global mostrado en el EDA es descriptivo.

El dataset supervisado contiene 4.022 fechas utilizables. Se excluyen las
primeras 60 ruedas por el historial requerido para las características y las
últimas cinco porque todavía carecen de una ventana futura completa.

| Conjunto | Filas | Fechas de emisión de la alerta |
|---|---:|---|
| Entrenamiento y validación cruzada | 3.212 | `2010-09-27` a `2023-06-30` |
| Separación temporal | 5 | Ruedas excluidas entre entrenamiento y prueba |
| Hold-out final | 805 | `2023-07-11` a `2026-09-23` |

Dentro del entrenamiento se usa `TimeSeriesSplit` con cinco pliegues
expansivos y `gap=5`. La separación evita que las ventanas futuras usadas
para etiquetar el entrenamiento alcancen el bloque de validación. Cada
pliegue calcula su P80 con su propio tramo de entrenamiento y aplica ese
mismo valor a su validación. El hold-out se reserva para la evaluación final
del ganador y el segundo mejor.

`src/pipeline.py` centraliza la imputación por mediana y el escalado de las
17 características numéricas, junto con la codificación one-hot de
`DIA_SEMANA`. El preprocesamiento se ajusta con las filas de entrenamiento
de cada pliegue y se aplica a las filas de validación.

## Métricas previstas

- **Técnica.** ROC-AUC medio y desviación entre pliegues para comparar los
  modelos. El recall de la clase alta se usará para diagnosticar alertas omitidas.
- **De negocio.** Diferencia de capital final frente a Buy & Hold en la
  simulación de la regla de reducción de exposición. El máximo drawdown
  complementará la comparación.