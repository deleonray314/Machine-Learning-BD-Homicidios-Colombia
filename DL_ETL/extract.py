import pandas as pd
import requests as re
import logging
from sodapy import Socrata

def fetch_api_json(url, limit=50000):
    """Descarga datos JSON desde una API pública con paginación."""
    logging.info(f"Descargando datos desde {url}")
    offset = 0
    all_data = []
    while True:
        params = {"$limit": limit, "$offset": offset}
        response = re.get(url, params=params)
        if response.status_code != 200:
            logging.error(f"Error {response.status_code} al consultar API: {url}")
            break
        data = response.json()
        if not data:
            break
        all_data.extend(data)
        offset += limit
        logging.info(f"Descargadas {len(all_data)} filas hasta ahora")
    return pd.DataFrame(all_data)

def fetch_homicidios_data(limit=340000):
    """Descarga los registros de Homicidios desde datos.gov.co"""
    logging.info("Descargando datos de homicidios desde Socrata...")
    client = Socrata("www.datos.gov.co", None)
    result = client.get("m8fd-ahd9", limit=limit)
    df_hom = pd.DataFrame.from_records(result)
    logging.info(f"Cantidad de registros descargados: {len(df_hom)}")
    return df_hom
