import streamlit as st

# 1. Configuración de la pestaña del navegador
st.set_page_config(
    page_title="Análisis CNMH - Equipo 1",
    page_icon="🇨🇴",
    layout="wide"
)

# 2. Estilo personalizado (Opcional para que se vea más limpio)
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stTitle {
        color: #2e4053;
        font-family: 'Helvetica', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Título Principal
st.title("🇨🇴 Observatorio de Memoria y Conflicto")
st.subheader("Análisis de Modalidades de Violencia en Colombia")

# 4. Introducción Narrativa (Muy importante para la exposición)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Objetivo dl Proyecto
    Mediante estos dasboard interactivos podremos visualizar algunos **patrones temporales y geográficos** de los hechos victimizantes 
    registrados por el **Centro Nacional de Memoria Histórica (CNMH)**. 
    
    A travs de este análisis, buscamos:
    * Visibilizar las tendencias en msacres y desaparición forzada.
    * Entender el impacto del reclutamiento de menores y ataques a civiles.
    * Proveer herramientas de datos para la construcción de memoria histórica.
    """)
    

with col2:
    # Espacio para los integrantes del equipo
    st.markdown("### Equipo de Aprendizaje 1")
    st.write("- [Sergio ]")
    st.write("- [Santiago castañeda ]")
    st.write("- [Juan Jose Moreno ]")
    st.caption("Programa: ADSO - SENA")

st.divider()

# 5. Resumen General (Métricas rápidas)
st.markdown("### Panorama General de los Datos")
# Aquí puedes poner métricas globales si ya cargaste un dataset general
c1, c2, c3 = st.columns(3)
c1.metric("Fuente", "CNMH")
c2.metric("País", "Colombia")
c3.metric("Herramientas", "Python / Streamlit")

# 6. Un mensaje final de cierre de portada
st.success("A ocntinuacion en lado izquierdo podr navegar por los panorams")