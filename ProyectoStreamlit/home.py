import streamlit as st  # Para visualización de proyectos de ML
import pandas as pd # Para manipular datos
import json # Para crear el mapa
import time # Para simular el tiempo de carga y mostrar un spinner

# --- NOMBRES DE ARCHIVOS GLOBALES ---
FILE_NAME = "HOMICIDIO_20251014.csv"
GEOJSON_FILE = "colombia.geo.json"

# =========================================================================
# 💡 FUNCIONES DE CARGA Y LIMPIEZA
# =========================================================================

# Usamos st.cache_data para acelerar la carga si se refresca la página
@st.cache_data
def load_and_clean_data(file_path):
    """Carga y limpia el dataset de homicidios."""
    try:
        df = pd.read_csv(file_path)
        df['FECHA HECHO'] = pd.to_datetime(df['FECHA HECHO'], dayfirst=True, errors='coerce')
        df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0).astype(int)
        df.dropna(subset=['FECHA HECHO', 'DEPARTAMENTO'], inplace=True)
        df['ANIO'] = df['FECHA HECHO'].dt.year
        df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.upper().str.strip()
        df['MUNICIPIO'] = df['MUNICIPIO'].str.title().str.strip() 
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo {file_path}. Asegúrate de que esté en la raíz.")
        return pd.DataFrame() 

@st.cache_data
def load_geojson_data(file_path):
    """Carga el archivo GeoJSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        return geojson
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo GeoJSON en la ruta {file_path}.")
        return None

# =========================================================================
# 🌐 ESTRUCTURA DE LA PORTADA
# =========================================================================

st.set_page_config(
    page_title="Página de Inicio | Análisis de Homicidios",
    page_icon="🤖",
    layout="wide"
)

st.title("🛡️ Proyecto de Machine Learning para la Prevención del Homicidio en Colombia")
st.markdown("---")
st.header("1. Contexto del Proyecto y Fuente de Datos")
st.markdown("""
Este proyecto tiene como objetivo principal aplicar técnicas de **Análisis de Datos y Machine Learning (ML)** para estudiar y modelar la dinámica del homicidio en Colombia.
""")

# --- LÓGICA DE CARGA Y ALMACENAMIENTO DE DATOS EN SESSION STATE ---

# Condición: Solo cargamos si el DataFrame principal no existe en la sesión
if 'df_homicidios' not in st.session_state:
    st.subheader("🚀 Inicializando el motor de datos...")
    
    with st.spinner('Cargando y limpiando datos... Esto puede tardar unos segundos...'):
        # 1. Cargar datos
        df_homicidios = load_and_clean_data(FILE_NAME)
        geojson_data = load_geojson_data(GEOJSON_FILE)
        
        # 2. Guardar en Session State
        if not df_homicidios.empty and geojson_data is not None:
            st.session_state['df_homicidios'] = df_homicidios
            st.session_state['geojson_data'] = geojson_data
            st.session_state['FILE_NAME'] = FILE_NAME # Guarda el nombre para la info.
            st.success("¡Datos cargados exitosamente! Ya puedes navegar al Dashboard Principal.")
        else:
            st.error("Error crítico: No se pudieron cargar los datos o el GeoJSON. Revisa los nombres de los archivos.")
            st.stop()
else:
    st.success("¡Datos listos! Continúa la navegación.")

# --- OBJETIVOS Y COMPONENTES (Contenido estático de la portada) ---

st.header("2. Objetivos del Análisis y Modelo de ML")
# ... (El resto del contenido de la portada se mantiene igual aquí) ...
# ... (Por brevedad, omitido en esta respuesta, pero debe ir completo) ...
# ... (Asegúrate de copiar el resto del código de la portada aquí) ...