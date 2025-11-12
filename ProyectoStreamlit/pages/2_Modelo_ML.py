import streamlit as st  # Para visualización de proyectos de ML
import pandas as pd # Para manipular datos
import plotly.express as px # Para graficar datos
from prophet import Prophet # Para realizar pronósticos de series temporales
from prophet.plot import plot_plotly # Para método de visualización dentro de la biblioteca de pronósticos Prophet
import matplotlib.pyplot as plt # Importar matplotlib para plot_components

# =========================================================================
# 🚨 VERIFICACIÓN Y RECUPERACIÓN DE DATOS
# =========================================================================
st.set_page_config(
    page_title="Modelo Predictivo | Análisis de Homicidios",
    page_icon="🔮",
    layout="wide"
)

if 'df_homicidios' not in st.session_state:
    st.error("Error: Los datos no se han cargado. Vuelve a la página de Inicio.")
    st.stop()

df_homicidios = st.session_state['df_homicidios']

# =========================================================================
# 💡 FILTROS DE ML (BARRA LATERAL)
# =========================================================================

st.sidebar.title("🛠️ Opciones del Modelo")

lista_departamentos = sorted(df_homicidios['DEPARTAMENTO'].unique())
selected_depto = st.sidebar.selectbox('1. Selecciona Departamento', options=lista_departamentos, index=0)

# Filtrar municipios basado en el departamento seleccionado
df_municipios = df_homicidios[df_homicidios['DEPARTAMENTO'] == selected_depto]
lista_municipios = sorted(df_municipios['MUNICIPIO'].unique())
selected_municipio = st.sidebar.selectbox('2. Selecciona Municipio para Predicción', options=lista_municipios)

prediction_months = st.sidebar.slider(
    '3. Meses a predecir:',
    min_value=3, 
    max_value=24, 
    value=12, 
    step=1
)

st.title(f"🔮 Modelo Predictivo: {selected_municipio}, {selected_depto}")
st.markdown("---")

# =========================================================================
# 1. PREPARACIÓN DE DATOS PARA PROPHET (FUNCIÓN AGREGADORA)
# =========================================================================

@st.cache_data
def prepare_prophet_data(df, municipio):
    """Filtra y agrega los datos por mes para un municipio específico."""
    
    # 1. Filtrar por municipio
    df_filtrado = df[df['MUNICIPIO'] == municipio].copy()

    # 2. Agregar por mes
    df_filtrado['FECHA HECHO'] = pd.to_datetime(df_filtrado['FECHA HECHO'])
    df_series = df_filtrado.groupby(pd.Grouper(key='FECHA HECHO', freq='M'))['CANTIDAD'].sum().reset_index()
    
    # 3. Preparar formato Prophet
    df_prophet = pd.DataFrame()
    df_prophet['ds'] = df_series['FECHA HECHO']
    df_prophet['y'] = df_series['CANTIDAD']
    
    # Asegurarse de que no haya meses vacíos (Prophet maneja esto mejor)
    df_prophet = df_prophet.dropna()
    
    if df_prophet.empty or len(df_prophet) < 24: # Se necesitan datos suficientes para estacionalidad
        return pd.DataFrame(), False
    
    return df_prophet, True

df_prophet, is_data_valid = prepare_prophet_data(df_homicidios, selected_municipio)

if not is_data_valid:
    st.warning(f"No hay suficientes datos históricos (mínimo 2 años) o el municipio '{selected_municipio}' tiene pocos registros para entrenar el modelo Prophet.")
    st.stop()


st.header("1. Datos de Serie de Tiempo")
st.caption(f"Datos históricos mensuales utilizados para entrenar el modelo en {selected_municipio}.")
st.dataframe(df_prophet.tail(), use_container_width=True)


# =========================================================================
# 2. ENTRENAMIENTO DEL MODELO Y PREDICCIÓN (PROPHET)
# =========================================================================

st.header("2. Predicción a Futuro")
st.info(f"El modelo predecirá los homicidios para los próximos **{prediction_months}** meses en {selected_municipio}.")


# Usar st.cache_resource para almacenar el modelo entrenado
# La clave incluye el municipio para reentrenar solo si el municipio cambia
@st.cache_resource
def train_prophet_model(df, municipio):
    """Entrena el modelo Prophet y realiza la predicción."""
    # Inicializar y ajustar el modelo
    model = Prophet(
        yearly_seasonality=True, 
        weekly_seasonality=False, 
        daily_seasonality=False
    )
    model.fit(df)
    return model

with st.spinner(f"Entrenando Modelo Prophet para {selected_municipio}..."):
    # Pasamos el nombre del municipio como argumento para el cache
    m = train_prophet_model(df_prophet, selected_municipio)

# Definir cuántos periodos futuros queremos predecir
future = m.make_future_dataframe(periods=prediction_months, freq='M')
forecast = m.predict(future)

# =========================================================================
# 3. VISUALIZACIÓN DE RESULTADOS
# =========================================================================
st.header("3. Gráfico de Predicción")

# Gráfico de Tendencia, Realidad y Predicción
fig1 = plot_plotly(m, forecast)
fig1.update_layout(
    title=f'Predicción de Homicidios Totales en {selected_municipio}',
    yaxis_title='Homicidios Totales',
    xaxis_title='Fecha'
)
st.plotly_chart(fig1, use_container_width=True)

# Desglose de la Predicción
st.subheader("Desglose de la Predicción (Próximos Meses)")

future_dates = forecast['ds'] > df_prophet['ds'].max()
df_forecast_future = forecast[future_dates][['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
df_forecast_future.columns = ['Fecha', 'Predicción (Media)', 'Intervalo Bajo (80%)', 'Intervalo Alto (80%)']
df_forecast_future['Fecha'] = df_forecast_future['Fecha'].dt.strftime('%Y-%m')

st.dataframe(df_forecast_future.reset_index(drop=True), use_container_width=True)

# =========================================================================
# 4. COMPONENTES DEL MODELO
# =========================================================================
st.header("4. Componentes del Modelo")

# Generar el gráfico de componentes de Prophet
# Nota: Usamos una figura de Matplotlib (fig2) para esto.
fig_components = m.plot_components(forecast)
st.pyplot(fig_components)