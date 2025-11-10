import pandas as pd
import logging
import unicodedata

def val(df_hom):
    """Valida y normaliza los datos de homicidios."""
    logging.info("Validando y preparando los datos...")

    expected_col = [
        "fecha_hecho", "cod_depto", "departamento",
        "cod_muni", "municipio", "zona", "sexo", "cantidad"
    ]

    rename_map = {
        "fecha": "fecha_hecho",
        "fechahecho": "fecha_hecho",
        "depart": "departamento",
        "depto": "cod_depto",
        "coddepartamento": "cod_depto",
        "codigo_departamento": "cod_depto",
        "codigo_municipio": "cod_muni",
        "codigomunicipio": "cod_muni",
        "municipio": "municipio",
        "zona": "zona",
        "sexo": "sexo",
        "cantidad": "cantidad",
        "total": "cantidad"
    }

    clean_cols = {col.lower().replace(" ", "").replace("_", ""): col for col in df_hom.columns}
    cols_to_rename = {}
    for simple_col, original_col in clean_cols.items():
        if simple_col in rename_map and rename_map[simple_col] not in df_hom.columns:
            cols_to_rename[original_col] = rename_map[simple_col]

    if cols_to_rename:
        logging.info(f"Renombrando columnas detectadas: {cols_to_rename}")
        df_hom = df_hom.rename(columns=cols_to_rename)

    missing_cols = [c for c in expected_col if c not in df_hom.columns]
    if missing_cols:
        raise ValueError(f"Faltan columnas obligatorias: {missing_cols}")

    # Conversión de tipos
    df_hom["fecha_hecho"] = pd.to_datetime(df_hom["fecha_hecho"], errors="coerce").dt.date
    df_hom["cantidad"] = pd.to_numeric(df_hom["cantidad"], errors="coerce").fillna(0).astype(int)

    # Normalización de texto
    for col in ["zona", "sexo", "departamento", "municipio"]:
        if col in df_hom.columns:
            df_hom[col] = (
                df_hom[col]
                .astype(str)
                .apply(lambda x: ''.join(
                    c for c in unicodedata.normalize('NFKD', x)
                    if not unicodedata.combining(c)
                ))
                .str.strip()
                .str.lower()
                .str.title()
            )

    return df_hom
