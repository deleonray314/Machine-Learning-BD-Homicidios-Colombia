import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cargar .env
load_dotenv()
logging.info("Archivo .env cargado correctamente")

# Variables de entorno
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

# Crear engine de conexión
try:
    engine = create_engine(
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        pool_recycle=3600
    )
    with engine.connect() as conn:
        logging.info("Conexión establecida con éxito a la base de datos.")
except Exception as e:
    logging.error(f"Error al conectar con la base de datos: {e}")
    engine = None
