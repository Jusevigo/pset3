
import os
import hashlib
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Configuración
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "snapshots"
OUTPUT_FILE = OUTPUT_DIR / "aapl_daily_obt.csv"

load_dotenv(ROOT / ".env")

required_vars = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]

missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    raise ValueError(
        f"Faltan variables en .env: {', '.join(missing)}"
    )


# --------------------------------------------------
# 2. Conexión y extracción
# --------------------------------------------------

connection = None

try:
    connection = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    query = """
        SELECT *
        FROM PSET2_DB.OBT.AAPL_DAILY_OBT
        ORDER BY TRADE_DATE
    """

    cursor = connection.cursor()

    try:
        cursor.execute(query)
        df = cursor.fetch_pandas_all()
    finally:
        cursor.close()

finally:
    if connection is not None:
        connection.close()


# --------------------------------------------------
# 3. Validaciones básicas
# --------------------------------------------------

if df.empty:
    raise ValueError("La extracción no devolvió registros.")

expected_columns = {
    "DATE_KEY",
    "TRADE_DATE",
    "CALENDAR_YEAR",
    "CALENDAR_QUARTER",
    "MONTH_NUMBER",
    "MONTH_NAME",
    "DAY_OF_MONTH",
    "DAY_OF_WEEK_ISO",
    "DAY_NAME",
    "SYMBOL_KEY",
    "SYMBOL",
    "CLOSE_PRICE",
    "SOURCE",
    "INGESTED_AT",
}

missing_columns = expected_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Faltan columnas esperadas: {missing_columns}"
    )

if df["TRADE_DATE"].isna().any():
    raise ValueError("Existen fechas nulas.")

if df["CLOSE_PRICE"].isna().any():
    raise ValueError("Existen precios de cierre nulos.")

if df.duplicated(["SYMBOL", "TRADE_DATE"]).any():
    raise ValueError("Existen duplicados en SYMBOL + TRADE_DATE.")


# --------------------------------------------------
# 4. Guardar snapshot
# --------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

# SHA-256 del archivo generado
sha256 = hashlib.sha256(OUTPUT_FILE.read_bytes()).hexdigest()


# --------------------------------------------------
# 5. Resumen de extracción
# --------------------------------------------------

print("\nEXTRACCIÓN COMPLETADA")
print("-" * 45)
print(f"Archivo: {OUTPUT_FILE}")
print(f"Filas: {len(df):,}")
print(f"Columnas: {len(df.columns)}")
print(f"Fecha inicial: {df['TRADE_DATE'].min()}")
print(f"Fecha final: {df['TRADE_DATE'].max()}")
print(f"Símbolos: {df['SYMBOL'].unique().tolist()}")
print(f"Duplicados: {df.duplicated(['SYMBOL', 'TRADE_DATE']).sum()}")
print(f"SHA-256: {sha256}")
