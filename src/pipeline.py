from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def crear_preprocesador(columnas_numericas):
    numericas = Pipeline([
        ("imputacion", SimpleImputer(strategy="median")),
        ("escalado", StandardScaler()),
    ])

    return ColumnTransformer([
        ("numericas", numericas, columnas_numericas),
        ("calendario", OneHotEncoder(handle_unknown="ignore"), ["MES"]),
    ])


def crear_pipeline(modelo, columnas_numericas):
    return Pipeline([
        ("preprocesamiento", crear_preprocesador(columnas_numericas)),
        ("modelo", modelo),
    ])