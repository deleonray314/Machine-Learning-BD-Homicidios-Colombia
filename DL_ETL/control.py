from sqlalchemy import text

def get_last_loaded_date(conn):
    result = conn.execute(
        text("SELECT last_loaded_date FROM etl_control WHERE proceso='homicidios_api'")
    ).fetchone()
    return result[0] if result else None

def update_last_loaded_date(conn, date_val):
    conn.execute(
        text("""
        INSERT INTO etl_control (proceso, last_loaded_date)
        VALUES ('homicidios_api', :d)
        ON DUPLICATE KEY UPDATE last_loaded_date = :d
        """),
        {"d": date_val},
    )
