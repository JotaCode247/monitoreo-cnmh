import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# Configuración del encabezado y dasboarad"
st.set_page_config(page_title="Tablero de Masacres - CNMH", layout="wide", page_icon="📊")

# --- aca damos estilo, se usa formato css ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7d32, #1b5e20); color: white; }
    h1, h2, h3 { color: #1a5276; font-family: 'Segoe UI', sans-serif; }
    .explicacion { font-size: 1.1rem; color: #566573; line-height: 1.6; border-left: 5px solid #1a5276; padding-left: 15px; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- aqui llamo los datos  ---
@st.cache_data
def load_data():
    # Cargamos los Excel con openpyxl
    df_c = pd.read_excel("data/CasosMA_202509.xlsx", engine='openpyxl')
    df_v = pd.read_excel("data/VictimasMA_202509.xlsx", engine='openpyxl')
    return df_c, df_v

df_casos, df_victimas = load_data()

# --- aqui agrego texto necesrio ---
st.title("📊 Observatorio de Memoria y Conflicto")
st.markdown("## Análisis Estadístico de Masacres en el Conflicto Armado")

with st.container():
    st.markdown("""
    <div class="explicacion">
    <b>¿Qué nos dicen estas cifras?</b><br>
    Las masacres son una de las modalidades más cruentas de la violencia en Colombia. Según el CNMH, estas acciones no solo 
    buscan la eliminación física de un grupo, sino el <b>control territorial mediante el terror</b>. Este tablero 
    permite identificar cómo las masacres se desplazan geográficamente y mutan en su intensidad a través de las décadas.
    </div>
    """, unsafe_allow_html=True)

# --- metodo slide para filtrsr barra laetrañ ---
st.sidebar.image("https://micrositios.centrodememoriahistorica.gov.co/observatorio/wp-content/themes/omc/img/logo-cnmh.png", width=200)
st.sidebar.header("Panel de Control")

# Filtro de Años
anios = sorted(df_casos['Año'].unique())
filtro_anio = st.sidebar.select_slider("Seleccione Rango de Tiempo", options=anios, value=(anios[0], anios[-1]))

# Filtro de Departamentos
deptos = sorted(df_casos['Departamento'].unique())
filtro_depto = st.sidebar.multiselect("Filtrar por Departamento", options=deptos, default=deptos)

# Filtro de Ciudad (Casca)
ciudades_disponibles = sorted(df_casos[df_casos['Departamento'].isin(filtro_depto)]['Municipio'].unique())
filtro_ciudad = st.sidebar.multiselect("Filtrar por Ciudad/Municipio", options=ciudades_disponibles, default=ciudades_disponibles)

# Aplicar filtros
df_c_f = df_casos[(df_casos['Año'] >= filtro_anio[0]) & (df_casos['Año'] <= filtro_anio[1]) & 
                (df_casos['Departamento'].isin(filtro_depto)) & (df_casos['Municipio'].isin(filtro_ciudad))]

df_v_f = df_victimas[(df_victimas['Año'] >= filtro_anio[0]) & (df_victimas['Año'] <= filtro_anio[1]) & 
                (df_victimas['Departamento'].isin(filtro_depto)) & (df_victimas['Municipio'].isin(filtro_ciudad))]

# --- aqui algunos indicadores (KPIs) ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Hechos Registrados", f"{len(df_c_f):,}")
c2.metric("Víctimas Totales", f"{len(df_v_f):,}")
c3.metric("Municipios Afectados", f"{df_c_f['Municipio'].nunique()}")
promedio = round(len(df_v_f)/len(df_c_f), 1) if len(df_c_f) > 0 else 0
c4.metric("Intensidad (Víctimas/Caso)", promedio)

st.divider()

# --- se dibuja el mapa con barras  ---
st.subheader("📍 Georreferenciación de Hechos")
st.markdown("Cada punto representa un evento de masacre. La altura y el color indican la concentración de hechos.")

# Configuración del mapa Pydeck
view_state = pdk.ViewState(latitude=4.57, longitude=-74.3, zoom=5, pitch=45)

layer = pdk.Layer(
    "HexagonLayer",
    df_c_f,
    get_position=['Longitud', 'Latitud'],
    radius=5000,
    elevation_scale=100,
    elevation_range=[0, 3000],
    pickable=True,
    extruded=True,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "Concentración de eventos en esta zona"}
))

# --- GRÁFICOS CONCISOS ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📈 Tendencia Histórica")
    resumen_anio = df_v_f.groupby('Año').size().reset_index(name='Víctimas')
    fig_line = px.area(resumen_anio, x='Año', y='Víctimas', 
                    title="Víctimas registradas por año",
                    color_discrete_sequence=['#1a5276'])
    fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

with col_der:
    st.subheader("🏙️ Top 10 Municipios más Afectados")
    resumen_muni = df_c_f.groupby('Municipio').size().reset_index(name='Casos')
    resumen_muni = resumen_muni.sort_values('Casos', ascending=False).head(10)
    fig_bar = px.bar(resumen_muni, x='Casos', y='Municipio', 
                    orientation='h', color='Casos',
                    color_continuous_scale='Blues')
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

# --- TABLA DE DETALLE ---
with st.expander("🔍 Ver base de datos detallada"):
    st.write("Filtre y ordene los datos directamente en la tabla:")
    st.dataframe(df_c_f[['ID Caso', 'Año', 'Municipio', 'Departamento', 'Total de Víctimas del Caso', 'Tipo de Armas']], use_container_width=True)