import streamlit as st  # Para visualización de proyectos de ML
import pandas as pd # Para manipular datos
import plotly.express as px # Para graficar datos
import json # Para crear el mapa
import base64   # convierte datos binarios en una cadena de caracteres de texto ASCII para transmitirlos de forma segura a través de sistemas que solo admiten texto, como el correo electrónico o HTTP

# =========================================================================
# 🚨 VERIFICACIÓN Y RECUPERACIÓN DE DATOS (CRÍTICO)
# =========================================================================
st.set_page_config(
    page_title="Dashboard Principal | Análisis de Homicidios",
    page_icon="🚨",
    layout="wide"
)

if 'df_homicidios' not in st.session_state:
    st.error("Error: Los datos no se han cargado. Por favor, vuelve a la página de Inicio para cargarlos.")
    st.stop()

# Recuperar datos y GeoJSON de la sesión
df_homicidios = st.session_state['df_homicidios']
geojson = st.session_state['geojson_data']

# --- Función y Variables auxiliares (DEFINIDAS DESPUÉS DE LA RECUPERACIÓN) ---
@st.cache_data
def convert_df_to_csv(df):
    """Convierte el DataFrame a un string CSV codificado para el botón de descarga."""
    return df.to_csv(index=False).encode('utf-8')

# =========================================================================
# 💡 FILTROS (BARRA LATERAL)
# =========================================================================

st.sidebar.title("🔍 Opciones de Filtrado")
min_year_total = int(df_homicidios['ANIO'].min())
max_year_total = int(df_homicidios['ANIO'].max())

year_range = st.sidebar.slider('Selecciona Rango de Años', min_value=min_year_total, max_value=max_year_total, value=(min_year_total, max_year_total), step=1)
lista_departamentos = sorted(df_homicidios['DEPARTAMENTO'].unique())

selected_departamentos = st.sidebar.multiselect('1. Selecciona Departamento(s)', options=lista_departamentos, default=[])

# APLICACIÓN DE FILTROS INICIALES (AÑO Y DEPARTAMENTO)
df_filtrado_base = df_homicidios[
    (df_homicidios['ANIO'] >= year_range[0]) & (df_homicidios['ANIO'] <= year_range[1])
]

if selected_departamentos:
    df_filtrado_base = df_filtrado_base[df_filtrado_base['DEPARTAMENTO'].isin(selected_departamentos)]

# Filtro de Municipios (DINÁMICO)
st.sidebar.markdown("---")
st.sidebar.subheader("Afinar por Municipio")

lista_municipios = sorted(df_filtrado_base['MUNICIPIO'].unique())

# El st.multiselect ya funciona como un buscador eficiente para listas grandes.
# Lo mantenemos, pero con un default vacío para que el usuario filtre por nombre.
selected_municipios = st.sidebar.multiselect(
    '2. Selecciona Municipio(s) (Busca por nombre)', 
    options=lista_municipios, 
    default=[], # Empezar vacío para que la selección de Departamento muestre el total
    key='multiselect_municipio' # Clave para evitar posibles conflictos de cache
)

# APLICACIÓN DEL FILTRO FINAL DE MUNICIPIO
df_filtrado = df_filtrado_base.copy() 

if selected_municipios:
    df_filtrado = df_filtrado[df_filtrado['MUNICIPIO'].isin(selected_municipios)]


# =========================================================================
# 📊 PÁGINA PRINCIPAL Y KPIs
# =========================================================================

st.title("🚨 Análisis de Homicidios en Colombia")
st.markdown(f"**Periodo de Análisis (Seleccionado en el Slider):** Desde **{year_range[0]}** hasta **{year_range[1]}**")

# --- CÁLCULO DE MÉTRICAS CLAVE A PARTIR DE df_filtrado ---
total_homicidios = df_filtrado['CANTIDAD'].sum()
min_anio_f = int(df_filtrado['ANIO'].min())
max_anio_f = int(df_filtrado['ANIO'].max())

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Homicidios (Filtro)", value=f"{total_homicidios:,}")

with col2:
    st.metric(label="Rango de Años con Datos", value=f"{min_anio_f} - {max_anio_f}")

# Calcular el departamento con más homicidios DENTRO DE LOS DATOS FILTRADOS
top_depto_data = df_filtrado.groupby('DEPARTAMENTO')['CANTIDAD'].sum().nlargest(1)
if not top_depto_data.empty:
    top_depto = top_depto_data.index[0]
    top_depto_cant = top_depto_data.values[0]
else:
    top_depto = "N/A"
    top_depto_cant = 0

with col3:
    st.metric(
        label="Más Afectado (Depto/Mpio)", 
        value=top_depto,
        delta=f"{top_depto_cant:,} casos"
    )

st.divider()

# =========================================================================
# 🌎 MAPA COROPLÉTICO 
# =========================================================================

if geojson is not None:
    st.header("🌎 Mapa de Homicidios por Departamento")
    df_mapa = df_filtrado.groupby('DEPARTAMENTO')['CANTIDAD'].sum().reset_index()
    df_mapa.rename(columns={'CANTIDAD': 'HOMICIDIOS_TOTAL'}, inplace=True)
    
    try:
        fig_mapa = px.choropleth(
            df_mapa,
            geojson=geojson,
            locations='DEPARTAMENTO', 
            featureidkey='properties.NOMBRE_DPT', 
            color='HOMICIDIOS_TOTAL', 
            color_continuous_scale="Reds", 
            center={"lat": 4.5, "lon": -74.0},
            title='Homicidios Acumulados por Departamento',
            hover_name='DEPARTAMENTO'
        )
        
        fig_mapa.update_geos(lataxis_range=[0, 14], lonaxis_range=[-80, -66], visible=False)
        fig_mapa.update_layout(margin={"r":0,"t":50,"l":0,"b":0}) 
        
        st.plotly_chart(fig_mapa, use_container_width=True)
    
    except ValueError as e:
        st.error(f"Error al generar el mapa. Problema: {e}")

st.divider()

# =========================================================================
# 📈 TENDENCIAS Y DISTRIBUCIONES 
# =========================================================================

tab1, tab2 = st.tabs(["Tendencia y Distribución", "Ranking Top/Bottom 10"])

with tab1:
    # Gráfico de Tendencia
    st.subheader("Tendencia de Homicidios (Datos Filtrados)")
    df_tendencia = df_filtrado.groupby('ANIO')['CANTIDAD'].sum().reset_index()
    fig_tendencia = px.line(df_tendencia, x='ANIO', y='CANTIDAD', title='Total de Homicidios por Año', labels={'ANIO': 'Año', 'CANTIDAD': 'Cantidad de Homicidios'}, markers=True)
    st.plotly_chart(fig_tendencia, use_container_width=True)

    st.divider()
    
    # Distribución por Categorías
    col4, col5 = st.columns(2)

    with col4:
        st.subheader("Distribución por Sexo")
        df_sexo = df_filtrado.groupby('SEXO')['CANTIDAD'].sum().reset_index()
        fig_sexo = px.pie(df_sexo, values='CANTIDAD', names='SEXO', title='Proporción por Sexo', hole=0.3)
        st.plotly_chart(fig_sexo, use_container_width=True)

    with col5:
        st.subheader("Distribución por Zona")
        df_zona = df_filtrado.groupby('ZONA')['CANTIDAD'].sum().reset_index()
        fig_zona = px.bar(df_zona, x='ZONA', y='CANTIDAD', title='Casos por Zona (Urbana vs. Rural)', color='ZONA')
        st.plotly_chart(fig_zona, use_container_width=True)

with tab2:
    st.header("Ranking de Municipios Más y Menos Afectados")
    
    # Agrupación por Municipio
    df_ranking = df_filtrado.groupby('MUNICIPIO')['CANTIDAD'].sum().reset_index()
    df_ranking.rename(columns={'CANTIDAD': 'HOMICIDIOS_TOTAL'}, inplace=True)

    col6, col7 = st.columns(2)

    # --- TOP 10 MÁS AFECTADOS ---
    with col6:
        st.subheader("🥇 Top 10 Municipios con Más Homicidios")
        df_top10 = df_ranking.nlargest(10, 'HOMICIDIOS_TOTAL')
        
        fig_top10 = px.bar(
            df_top10.sort_values(by='HOMICIDIOS_TOTAL', ascending=True),
            x='HOMICIDIOS_TOTAL', 
            y='MUNICIPIO', 
            orientation='h',
            title='Top 10 (Más Violentos)',
            color='HOMICIDIOS_TOTAL',
            color_continuous_scale=px.colors.sequential.Reds
        )
        st.plotly_chart(fig_top10, use_container_width=True)

    # --- TOP 10 MENOS AFECTADOS ---
    with col7:
        st.subheader("📉 Top 10 Municipios con Menos Homicidios")
        df_ranking_pos = df_ranking[df_ranking['HOMICIDIOS_TOTAL'] > 0]
        df_bottom10 = df_ranking_pos.nsmallest(10, 'HOMICIDIOS_TOTAL')
        
        fig_bottom10 = px.bar(
            df_bottom10.sort_values(by='HOMICIDIOS_TOTAL', ascending=False),
            x='HOMICIDIOS_TOTAL', 
            y='MUNICIPIO', 
            orientation='h',
            title='Top 10 (Menos Violentos, > 0 casos)',
            color='HOMICIDIOS_TOTAL',
            color_continuous_scale=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig_bottom10, use_container_width=True)
        st.caption("Nota: Este ranking excluye municipios que no reportaron casos en el periodo filtrado.")

st.divider()

# =========================================================================
# 📝 DESGLOSE DE DATOS Y EXPORTACIÓN
# =========================================================================

st.header("🔍 Desglose de Datos Filtrados por Detalle")

# 1. Crear el DataFrame de desglose
df_desglose = df_filtrado.groupby(['DEPARTAMENTO', 'MUNICIPIO', 'SEXO', 'ZONA'])['CANTIDAD'].sum().reset_index()
df_desglose.rename(columns={'CANTIDAD': 'HOMICIDIOS_TOTAL'}, inplace=True)
df_desglose.sort_values(by='HOMICIDIOS_TOTAL', ascending=False, inplace=True)

# 2. Mostrar la tabla dinámica
st.dataframe(df_desglose, use_container_width=True)

# 3. Preparar y Mostrar el Botón de Descarga
csv_data = convert_df_to_csv(df_desglose)

min_anio_f_file = int(df_filtrado['ANIO'].min())
max_anio_f_file = int(df_filtrado['ANIO'].max())

st.download_button(
    label="Descargar Desglose Filtrado (CSV)",
    data=csv_data,
    file_name=f'desglose_homicidios_{min_anio_f_file}_a_{max_anio_f_file}.csv',
    mime='text/csv',
)