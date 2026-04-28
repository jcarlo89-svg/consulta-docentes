import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Legajo Docente ETI", layout="wide")

# CSS Profesional para evitar textos cortados y mejorar el orden
st.markdown("""
    <style>
    .main { background-color: #f0f2f5; }
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #d1d9e6;
        margin-bottom: 20px;
    }
    .header-label {
        font-size: 11px;
        color: #888;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .docente-nombre {
        font-size: 22px;
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 5px;
    }
    .tag-especialidad {
        background-color: #004B98;
        color: white;
        padding: 6px 15px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 12px;
        display: inline-block;
    }
    .grado-item {
        margin-top: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }
    .grado-titulo {
        color: #00B5E2;
        font-weight: bold;
        font-size: 16px;
        text-transform: uppercase;
    }
    .grado-inst {
        color: #444;
        font-size: 13px;
    }
    .curso-box {
        background-color: #e9ecef;
        padding: 12px;
        border-radius: 5px;
        margin-top: 15px;
        font-size: 13px;
        color: #333;
        border-left: 5px solid #00B5E2;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Legajo Docente ETI")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

busqueda = st.text_input("Ingrese DNI o Apellidos para consultar:")

if busqueda:
    # Filtro de búsqueda
    res = df[(df['dni'].astype(str).str.contains(busqueda)) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not res.empty:
        # Agrupamos por docente para mostrar una sola ficha por persona
        for nombre, grupo in res.groupby('nombre'):
            dni_val = grupo['dni'].iloc[0]
            # Obtenemos especialidad y cursos (asegurando que no digan "nan")
            especialidad = str(grupo['especialidad'].iloc[0]) if 'especialidad' in grupo.columns and pd.notna(grupo['especialidad'].iloc[0]) else "No definida"
            cursos = str(grupo['cursos_dictados'].iloc[0]) if 'cursos_dictados' in grupo.columns and pd.notna(grupo['cursos_dictados'].iloc[0]) else "Sin cursos registrados"

            # Renderizado de la ficha del docente
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="header-label">Docente ETI</div>
                        <div class="docente-nombre">{nombre}</div>
                        <div class="header-label">Identificación: <span style="color:#333">DNI {dni_val}</span></div>
                    </div>
                    <div style="text-align: right;">
                        <div class="header-label">Especialidad</div>
                        <div class="tag-especialidad">{especialidad}</div>
                    </div>
                </div>
                
                <div style="margin-top: 25px;">
                    <div class="header-label">Historial Académico</div>
            """, unsafe_allow_html=True)

            # Bloque de Grados
            for _, row in grupo.iterrows():
                st.markdown(f"""
                    <div class="grado-item">
                        <div class="grado-titulo">{row['grado']}</div>
                        <div class="grado-inst">{row['institucion']} | <b>Año: {row['anio']}</b></div>
                    </div>
                """, unsafe_allow_html=True)

            # Bloque de Cursos
            st.markdown(f"""
                    <div style="margin-top: 20px;">
                        <div class="header-label">Cursos Dictados</div>
                        <div class="curso-box">
                            {cursos}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("No se encontraron resultados.")
