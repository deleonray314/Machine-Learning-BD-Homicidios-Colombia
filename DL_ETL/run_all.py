import logging
from datetime import datetime

from DL_ETL.config import engine
from DL_ETL.extract import fetch_api_json, fetch_homicidios_data
from DL_ETL.transform import val
from DL_ETL.load import upsert_raw
from DL_ETL.control import get_last_loaded_date, update_last_loaded_date

# =========================
# CARGAS DIMENSIONALES
# =========================
def load_depto(conn):
    url = "https://www.datos.gov.co/resource/vcjz-niiq.json"
    from DL_ETL.extract import fetch_api_json
    df_depto = fetch_api_json(url)
    if df_depto.empty:
        logging.warning("No se obtuvieron datos Departamentos.")
        return
    df_depto = df_depto.rename(columns={
        "codigo_departamento": "cod_depto",
        "nombre_departamento": "nom_depto"
    })[["cod_depto", "nom_depto"]].drop_duplicates()
    df_depto.to_sql("dim_departamentos", conn, if_exists="replace", index=False)
    logging.info(f"{len(df_depto)} registros insertados en dim_departamentos.")

def load_mpio(conn):
    url = "https://www.datos.gov.co/resource/gdxc-w37w.json"
    from DL_ETL.extract import fetch_api_json
    df_mpio = fetch_api_json(url)
    if df_mpio.empty:
        logging.warning("No se obtuvieron datos Municipios.")
        return
    df_mpio = df_mpio.rename(columns={
        "cod_dpto": "cod_depto",
        "dpto": "nom_depto",
        "cod_mpio": "cod_muni",
        "nombre_municipio": "nom_mpio"
    })[["cod_muni", "cod_depto", "nom_mpio"]].drop_duplicates()
    df_mpio.to_sql("dim_municipios", conn, if_exists="replace", index=False)
    logging.info(f"{len(df_mpio)} registros insertados en dim_municipios.")

# =========================
# PROCESO PRINCIPAL HOMICIDIOS
# =========================
def main_hom():
    logging.info("Iniciando ETL de Homicidios API...")
    df = fetch_homicidios_data()
    df = val(df)

    with engine.connect() as conn:
        last_date = get_last_loaded_date(conn)
        if last_date:
            if isinstance(last_date, str):
                last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
            df_filtrado = df[df["fecha_hecho"] > last_date]
            logging.info(f"Filtrando registros nuevos posteriores a {last_date}")
        else:
            df_filtrado = df

        if df_filtrado.empty:
            logging.info("No hay registros nuevos para cargar.")
            return

        upsert_raw(conn, df_filtrado)
        new_max_date = df_filtrado["fecha_hecho"].max()
        update_last_loaded_date(conn, new_max_date)
        logging.info(f"Carga completada. Última fecha cargada: {new_max_date}")

# =========================
# FUNCIÓN ORQUESTADORA FINAL
# =========================
def run_all_etl():
    logging.info("=== Iniciando flujo completo ETL (Data Lake) ===")
    if not engine:
        logging.error("Motor de conexión no inicializado. Abortando.")
        return

    try:
        with engine.connect() as conn:
            load_depto(conn)
            load_mpio(conn)
        main_hom()
    except Exception as e:
        logging.error(f"Error durante la ejecución del ETL: {e}")

    logging.info("=== Flujo ETL completado exitosamente ===")

if __name__ == "__main__":
    run_all_etl()
