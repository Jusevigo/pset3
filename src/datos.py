import os
from datetime import date
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]


def cargar_obt() -> pd.DataFrame:
    """Carga la OBT de AAPL hasta la fecha de corte inclusive."""
    load_dotenv(RAIZ_PROYECTO / ".env")

    fecha_corte = date.fromisoformat(os.environ["DATA_CUTOFF"])

    consulta = """
        SELECT *
        FROM PSET2_DB.OBT.AAPL_DAILY_OBT
        WHERE TRADE_DATE <= %s
        ORDER BY TRADE_DATE
    """

    with snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    ) as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (fecha_corte,))
            columnas = [columna[0] for columna in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columnas)

    df["TRADE_DATE"] = pd.to_datetime(df["TRADE_DATE"])
    return df