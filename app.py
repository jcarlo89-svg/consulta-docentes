import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Legajo Docente ETI", layout="wide")

# CSS para un diseño limpio, profesional y sin textos cortados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .legajo-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .header-label {
        font-size: 11px;
        color: #6c757d;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }
    .data-text {
        font-size: 14px;
        color: #212529;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .grado-resaltado {
        color: #00B5E2;
        font-weight: bold;
        font-size: 15px;
        text-transform: uppercase;
    }
    .especialidad-tag {
        display: inline-block;
        background-color: #004B98;
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
        margin-top: 5px;
    }
    .cursos-box {
        background-color: #f1f3f5;
        padding: 10px;
        border-left: 4px solid #00B5E2;
        font-size: 13px;
        margin-top: 10px;
        border-radius: 0 4px 4px 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Sistema de Legajo Docente ETI")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

busqueda = st.text_input("Ingrese DNI o Apellidos para consultar:")

if busqueda:
    # Filtro de búsqueda
    res = df[(df['dni'].astype(str).str.contains(busqueda)) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not res.empty:
        # Agrupamos por nombre para no repetir el bloque de "Datos del Docente"
        for nombre, grupo in res.groupby('nombre'):
            dni_docente = grupo['dni'].iloc[0]
            # Tomamos la especialidad del primer registro encontrado
            especialidad = grupo['especialidad'].iloc[0] if 'especialidad' in grupo.columns else "No especificada"
            
            with st.container():
                st.markdown(f"""
                <div class="legajo-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div class="header-label">Docente</div>
                            <div class="data-text" style="font-size: 18px; font-weight: bold;">{nombre}</div>
                            <div class="header-label">Identificación</div>
                            <div class="data-text">DNI {dni_docente}</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="header-label">Especialidad ETI</div>
                            <div class="especialidad-tag">{especialidad}</div>
                        </div>
                    </div>
                    
                    <hr style="margin: 15px 0;">
                    
                    <div class="header-label">Historial de Grados y Títulos</div>
                """, unsafe_allow_html=True)
                
                # Listamos cada grado en una línea independiente
                for _, row in grupo.iterrows():
                    st.markdown(f"""
                        <div style="margin-bottom: 15px; padding-left: 10px; border-left: 2px solid #eee;">
                            <div class="grado-resaltado">{row['grado']}</div>
                            <div class="data-text" style="font-size: 13px;">{row['institucion']} | Año: {row['anio']}</div>
                        </div>
                    """, unsafe_allow_html=True)

                # Columna independiente de cursos al final del legajo
                if 'cursos_dictados' in grupo.columns:
                    # Unimos todos los cursos mencionados en sus distintos grados si es necesario, 
                    # o solo mostramos los del docente
                    cursos = ", ".join(grupo['cursos_dictados'].dropna().unique())
                    if cursos:
                        st.markdown(f"""
                            <div class="header-label">Cursos Dictados</div>
                            <div class="cursos-box">{cursos}</div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("No se encontraron registros para la búsqueda realizada.")
