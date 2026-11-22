import pandas as pd

def construir_features(df_obt):
    mercado = df_obt.sort_values("TRADE_DATE").set_index("TRADE_DATE")
    cierre_ajustado = mercado["ADJ_CLOSE_PRICE"]
    retorno_pct = cierre_ajustado.pct_change(fill_method=None).mul(100)

    volumen_habitual = mercado["VOLUME"].shift(1).rolling(20).mean()
    apertura = mercado["OPEN_PRICE"]

    features = pd.DataFrame({
        "VOL_HIST_20": retorno_pct.rolling(20).std(ddof=1),
        "VOLUMEN_REL_20": mercado["VOLUME"].div(
            volumen_habitual.where(volumen_habitual > 0)
        ),
        "RANGO_INTRADIA_REL": (
            mercado["HIGH_PRICE"] - mercado["LOW_PRICE"]
        ).div(apertura.where(apertura > 0)),
    })

    for rezago in range(5):
        features[f"RET_LAG_{rezago}"] = retorno_pct.shift(rezago)

    features["ABS_RET_0"] = retorno_pct.abs()
    features["ABS_RET_1"] = retorno_pct.abs().shift(1)

    features["VOL_HIST_5"] = retorno_pct.rolling(5).std(ddof=1)
    features["VOL_HIST_60"] = retorno_pct.rolling(60).std(ddof=1)
    features["VOL_RATIO_5_20"] = features["VOL_HIST_5"].div(
        features["VOL_HIST_20"].where(features["VOL_HIST_20"] > 0)
    )

    for ventana in (20, 50):
        media_movil = cierre_ajustado.rolling(ventana).mean()
        features[f"DIST_SMA_{ventana}"] = cierre_ajustado.div(media_movil).sub(1)

    features["MOM_10"] = cierre_ajustado.pct_change(10, fill_method=None)

    cierre = mercado["CLOSE_PRICE"]
    factor_ajuste = cierre_ajustado.div(cierre.where(cierre > 0))
    apertura_ajustada = apertura.mul(factor_ajuste)
    features["GAP_APERTURA"] = apertura_ajustada.div(
        cierre_ajustado.shift(1)
    ).sub(1)

    features["MES"] = mercado.index.month
    return features