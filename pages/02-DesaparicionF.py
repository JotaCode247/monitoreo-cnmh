import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# 1. Configuración de la página
st.set_page_config(page_title="Desaparición Forzada - CNMH", layout="wide", page_icon="👤")


st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0; }
    .titulo-seccion { color: #1a5276; border-bottom: 2px solid #cb4335; padding-bottom: 5px; margin-top: 30px; }
    .contexto-df { background-color: #fdf2f2; padding: 20px; border-radius: 10px; border-left: 6px solid #cb4335; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS (LECTURA DE EXCEL) ---
@st.cache_data
def load_data_df():
    try:
        # Leemos los archivos Excel directamente
        df_c = pd.read_excel("data/CasosDF_202509.xlsx", engine='openpyxl')
        df_v = pd.read_excel("data/VictimasDF_202509.xlsx", engine='openpyxl')
        return df_c, df_v
    except Exception as e:
        st.error(f"Error al cargar los archivos: {e}")
        return None, None

df_casos, df_victimas = load_data_df()

if df_casos is not None and df_victimas is not None:

    st.title("👤 Análisis de Desaparición Forzada")
    st.markdown("""
    <div class="contexto-df">
        <h4>Perfil Demográfico y Territorial</h4>
        <p>La desaparición forzada afecta de manera diferenciada a la población según su edad y género. 
        Este tablero analiza quiénes son las víctimas y dónde se concentran los hechos mediante una 
        visualización de histograma espacial 3D.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR (FILTROS) ---
    st.sidebar.header("⚙️ Panel de Control")
    
    anios = sorted(df_casos['Año'].unique())
    rango_anio = st.sidebar.select_slider("Seleccione Periodo", options=anios, value=(anios[0], anios[-1]))
    
    deptos = sorted(df_casos['Departamento'].unique())
    deptos_sel = st.sidebar.multiselect("Filtrar Departamentos", options=deptos, default=deptos[:3])

    # Aplicar Filtros
    df_c_f = df_casos[(df_casos['Año'] >= rango_anio[0]) & (df_casos['Año'] <= rango_anio[1]) & (df_casos['Departamento'].isin(deptos_sel))]
    df_v_f = df_victimas[(df_victimas['Año'] >= rango_anio[0]) & (df_victimas['Año'] <= rango_anio[1]) & (df_victimas['Departamento'].isin(deptos_sel))]

    # --- KPIs ---
    st.markdown("<h3 class='titulo-seccion'>Cifras Consolidadas</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    total_v = len(df_v_f)
    c1.metric("Víctimas Totales", f"{total_v:,}")
    

    desap = len(df_v_f[df_v_f['Situación Actual de la Víctima'].str.contains('DESAPARECIDO', na=False)])
    c2.metric("Siguen Desaparecidos", f"{desap:,}", delta=f"{(desap/total_v*100):.1f}%", delta_color="inverse")
    
    hombres = len(df_v_f[df_v_f['Sexo'] == 'HOMBRE'])
    c3.metric("Víctimas Hombres", f"{hombres:,}")
    
    mujeres = len(df_v_f[df_v_f['Sexo'] == 'MUJER'])
    c4.metric("Víctimas Mujeres", f"{mujeres:,}")

    st.divider()


    st.subheader("🗺️ Histograma Espacial 3D (Concentración de Hechos)")
    st.info("La altura de las barras indica el número de víctimas en cada ubicación. Use 'Ctrl + Clic' para rotar el mapa.")
    
    view_state = pdk.ViewState(latitude=4.57, longitude=-74.3, zoom=5, pitch=45)

    layer_3d = pdk.Layer(
        "ColumnLayer",
        df_c_f,
        get_position=['Longitud', 'Latitud'],
        get_elevation="Total de Víctimas del Caso",
        elevation_scale=4000, 
        radius=2000,
        get_fill_color=[139, 0, 0, 200], # Rojo institucional CNMH
        pickable=True,
        extruded=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer_3d],
        initial_view_state=view_state,
        tooltip={"text": "Municipio: {Municipio}\nVíctimas: {Total de Víctimas del Caso}"}
    ))


    st.markdown("<h3 class='titulo-seccion'>Análisis de Población y Estado Actual</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("⚤ Género")
        fig_sexo = px.pie(df_v_f, names='Sexo', hole=0.4,
                         color_discrete_map={'HOMBRE': '#1a5276', 'MUJER': '#cb4335', 'SIN INFORMACION': '#d5dbdb'})
        st.plotly_chart(fig_sexo, use_container_width=True)

    with col2:
        st.subheader("🎂 Ciclo Vital (Edad)")
        # Gráfico de barras horizontales para que se lea mejor el texto de la edad
        edad_counts = df_v_f['Edad'].value_counts().reset_index()
        fig_edad = px.bar(edad_counts, x='count', y='Edad', orientation='h',
                         color='count', color_continuous_scale='Reds')
        fig_edad.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_edad, use_container_width=True)

    with col3:
        st.subheader("⌛ Situación Actual")
        situacion = df_v_f['Situación Actual de la Víctima'].value_counts().reset_index()
        fig_sit = px.bar(situacion, x='Situación Actual de la Víctima', y='count',
                        color_discrete_sequence=['#566573'])
        st.plotly_chart(fig_sit, use_container_width=True)

    # --- TABLA ---
    with st.expander("🔍 Detalle de la Base de Datos (Víctimas)"):
        st.dataframe(df_v_f[['ID Persona', 'Año', 'Municipio', 'Departamento', 'Sexo', 'Edad', 'Situación Actual de la Víctima']], use_container_width=True)

else:
    st.warning("⚠️ Cargue los archivos CasosDF_202509.xlsx y VictimasDF_202509.xlsx en la carpeta /data")