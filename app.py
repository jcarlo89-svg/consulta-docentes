import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Legajo Docente ETI", layout="wide")

# Estilo CSS para reducir tamaños y mejorar legibilidad
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .docente-container { 
        border-bottom: 1px solid #e0e0e0; 
        padding: 10px 0; 
        font-size: 12px; /* Letra más pequeña general */
    }
    .label-header { 
        font-weight: bold; 
        color: #333; 
        font-size: 11px; 
        text-transform: uppercase; 
    }
    .info-text { color: #555; margin-bottom: 5px; }
    .titulo-celeste { 
        color: #00B5E2; 
        font-weight: bold; 
        font-size: 13px; 
        text-transform: uppercase; 
    }
    .badge-especialidad {
        background-color: #f0f2f6;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: bold;
        color: #004B98;
        font-size: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Legajo Docente ETI")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

busqueda = st.text_input("Buscar por DNI o Apellidos:")

if busqueda:
    # Filtro flexible
    res = df[(df['dni'].astype(str) == busqueda) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not res.empty:
        for _, row in res.iterrows():
            with st.container():
                # Usamos columnas para distribuir el espacio
                c1, c2, c3 = st.columns([1.2, 2, 1.5])
                
                with c1:
                    st.markdown(f"<div class='label-header'>Graduado</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-text'><b>{row['nombre']}</b><br>DNI {row['dni']}</div>", unsafe_allow_html=True)
                    # Badge de especialidad
                    st.markdown(f"<span class='badge-especialidad'>{row.get('especialidad', 'General')}</span>", unsafe_allow_html=True)

                with c2:
                    st.markdown(f"<div class='label-header'>Grado o Título</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='titulo-celeste'>{row['grado']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-text' style='font-size:10px;'>Año: {row['anio']}</div>", unsafe_allow_html=True)
                    
                    # Mostrar cursos si existen
                    if 'cursos' in row and pd.notna(row['cursos']):
                        st.markdown(f"<div class='label-header' style='margin-top:5px;'>Cursos Dictados</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:11px; color:#666;'>{row['cursos']}</div>", unsafe_allow_html=True)

                with c3:
                    st.markdown(f"<div class='label-header'>Institución</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-text'>{row['institucion']}</div>", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin:10px 0; opacity:0.3;'>", unsafe_allow_html=True)
    else:
        st.warning("No se encontraron registros.")

# --- PANEL ADMIN (Opcional mantenerlo igual) ---
