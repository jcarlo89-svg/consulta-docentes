import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import re

# Configuración de la página
st.set_page_config(page_title="Legajo Docente ETI", layout="wide")

# Función para convertir links de Drive a links directos de imagen
def convertir_drive_url(url):
    if not url or pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    
    # Extraer el ID del archivo (formato estándar o formato de exportación)
    id_match = re.search(r'/d/([-\w]{25,})', str(url)) or re.search(r'id=([-\w]{25,})', str(url))
    
    if id_match:
        file_id = id_match.group(1)
        # Formato de URL directa para visualización en aplicaciones web
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    
    return url

# Estilos CSS personalizados
st.markdown("""
    <style>
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #d1d9e6;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .header-label { font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase; }
    .docente-nombre { font-size: 22px; font-weight: bold; color: #1a1a1a; margin-bottom: 2px; }
    .tag-especialidad { background-color: #004B98; color: white; padding: 6px 12px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .grado-item { margin-top: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
    .grado-titulo { color: #00B5E2; font-weight: bold; font-size: 15px; }
    .curso-box { background-color: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 5px solid #00B5E2; margin-top: 10px; font-size: 13px; }
    .foto-perfil { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid #00B5E2; }
    .contacto-tel { font-size: 14px; color: #25D366; font-weight: bold; display: flex; align-items: center; gap: 5px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Legajo Docente ETI")

# Conexión a la base de datos (Google Sheets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except Exception as e:
    st.error("Error al conectar con la base de datos. Verifica la configuración en secrets.")
    df = pd.DataFrame()

# Buscador
busqueda = st.text_input("Ingrese DNI o Apellidos para consultar:")

if busqueda and not df.empty:
    # Filtrado flexible por DNI o Nombre
    res = df[(df['dni'].astype(str).str.contains(busqueda)) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not res.empty:
        # Agrupamos por nombre para que los diferentes grados del mismo docente aparezcan en una sola ficha
        for nombre, grupo in res.groupby('nombre'):
            dni_val = grupo['dni'].iloc[0]
            especialidad = str(grupo['especialidad'].iloc[0]) if 'especialidad' in grupo.columns and pd.notna(grupo['especialidad'].iloc[0]) else "GENERAL"
            
            # Nuevo campo: Número telefónico
            telefono = str(grupo['numero'].iloc[0]) if 'numero' in grupo.columns and pd.notna(grupo['numero'].iloc[0]) else "No registrado"
            
            # Procesamiento de Foto
            raw_foto = str(grupo['foto'].iloc[0]) if 'foto' in grupo.columns and pd.notna(grupo['foto'].iloc[0]) else ""
            foto_url = convertir_drive_url(raw_foto)
            placeholder = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

            # Renderizado de la ficha principal
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 25px;">
                        <img src="{foto_url}" class="foto-perfil" onerror="this.src='{placeholder}'">
                        <div>
                            <div class="header-label">Docente ETI</div>
                            <div class="docente-nombre">{nombre}</div>
                            <div class="header-label">Identificación: DNI {dni_val}</div>
                            <div class="contacto-tel">📞 WhatsApp: {telefono}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="header-label">Especialidad</div>
                        <div class="tag-especialidad">{especialidad}</div>
                    </div>
                </div>
                <div style="margin-top: 25px; border-top: 1px solid #eee; padding-top: 15px;">
                    <div class="header-label">Historial Académico</div>
            """, unsafe_allow_html=True)

            # Listado de grados y títulos del docente
            for _, row in grupo.iterrows():
                st.markdown(f"""
                    <div class="grado-item">
                        <div class="grado-titulo">{row['grado']}</div>
                        <div style="font-size: 13px; color: #555;">{row['institucion']} | Año: {row['anio']}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Sección de Cursos Dictados (tomando los valores únicos del grupo)
            cursos_list = grupo['cursos_dictados'].dropna().unique()
            cursos_texto = " • ".join([str(c) for c in cursos_list]) if len(cursos_list) > 0 else "Sin cursos registrados"

            st.markdown(f"""
                    <div style="margin-top: 20px;">
                        <div class="header-label">Cursos Dictados</div>
                        <div class="curso-box">{cursos_texto}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No se encontraron resultados para la búsqueda ingresada.")
