import logging
from sqlalchemy import text

def upsert_raw(conn, df_hom):
    """Inserta datos en la tabla raw_homicidios."""
    logging.info("Insertando datos en la tabla raw_homicidios...")
    insert_sql = """
    INSERT INTO raw_homicidios
    (fecha_hecho, cod_depto, departamento, cod_muni, municipio, zona, sexo, cantidad, fuente)
    VALUES (:fecha_hecho, :cod_depto, :departamento, :cod_muni, :municipio, :zona, :sexo, :cantidad, 'API_HOMICIDIOS')
    ON DUPLICATE KEY UPDATE cantidad = VALUES(cantidad), fecha_ingreso = CURRENT_TIMESTAMP
    """
    rows = df_hom.to_dict(orient="records")
    for r in rows:
        conn.execute(text(insert_sql), r)
    logging.info(f"{len(df_hom)} registros procesados correctamente.")
