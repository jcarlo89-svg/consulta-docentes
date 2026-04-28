import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import re

# 1. Configuración de la página
st.set_page_config(page_title="Legajo Docente ETI", layout="wide")

# 2. Función de conversión de imagen (Versión Ultra-Estable)
def convertir_drive_url(url):
    if not url or pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    
    # Extraer el ID del archivo
    id_match = re.search(r'/d/([-\w]{25,})', str(url)) or re.search(r'id=([-\w]{25,})', str(url))
    
    if id_match:
        file_id = id_match.group(1)
        # Usamos el servidor de miniaturas de alta calidad para evitar bloqueos de visualización
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    
    return url

# 3. Estilos CSS Personalizados
st.markdown("""
    <style>
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #d1d9e6;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .docente-nombre { font-size: 24px; font-weight: bold; color: #1a1a1a; margin-bottom: 2px; }
    .header-label { font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    .tag-especialidad { background-color: #004B98; color: white; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: bold; }
    .contacto-tel { font-size: 15px; color: #25D366; font-weight: bold; margin-top: 10px; display: flex; align-items: center; gap: 8px; }
    .grado-item { margin-top: 15px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0; }
    .grado-titulo { color: #00B5E2; font-weight: bold; font-size: 16px; }
    .curso-box { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #00B5E2; margin-top: 10px; font-size: 14px; color: #333; }
    .foto-perfil { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 4px solid #00B5E2; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Legajo Docente ETI")

# 4. Conexión a Datos con manejo de errores
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except Exception as e:
    st.error("No se pudo conectar con el Google Sheet. Revisa los Secrets.")
    df = pd.DataFrame()

# 5. Buscador e Interfaz
busqueda = st.text_input("Ingrese DNI o Apellidos del docente:")

if busqueda and not df.empty:
    # Filtrado por DNI o Nombre (insensible a mayúsculas)
    res = df[(df['dni'].astype(str).str.contains(busqueda)) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not res.empty:
        for nombre, grupo in res.groupby('nombre'):
            # Datos principales
            dni_val = grupo['dni'].iloc[0] if 'dni' in grupo.columns else "N/A"
            especialidad = str(grupo['especialidad'].iloc[0]) if 'especialidad' in grupo.columns and pd.notna(grupo['especialidad'].iloc[0]) else "GENERAL"
            
            # --- Lógica para corregir el formato del número telefónico ---
            if 'numero' in grupo.columns:
                val_tel = grupo['numero'].iloc[0]
                if pd.notna(val_tel):
                    try:
                        # Convertimos de científico a entero limpio
                        telefono = str(int(float(val_tel)))
                    except:
                        telefono = str(val_tel)
                else:
                    telefono = "No registrado"
            else:
                telefono = "Columna 'numero' no encontrada"
            
            # Procesar foto
            raw_foto = str(grupo['foto'].iloc[0]) if 'foto' in grupo.columns and pd.notna(grupo['foto'].iloc[0]) else ""
            foto_url = convertir_drive_url(raw_foto)
            placeholder = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

            # HTML de la Ficha
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="display: flex; align-items: center; gap: 30px;">
                        <img src="{foto_url}" class="foto-perfil" onerror="this.src='{placeholder}'">
                        <div>
                            <div class="header-label">Docente ETI</div>
                            <div class="docente-nombre">{nombre}</div>
                            <div class="header-label">DNI: {dni_val}</div>
                            <div class="contacto-tel">📲 WhatsApp: {telefono}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="header-label">Especialidad</div>
                        <div class="tag-especialidad">{especialidad}</div>
                    </div>
                </div>
                <div style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    <div class="header-label">Trayectoria Académica</div>
            """, unsafe_allow_html=True)

            # Lista de grados
            for _, row in grupo.iterrows():
                st.markdown(f"""
                    <div class="grado-item">
                        <div class="grado-titulo">{row['grado']}</div>
                        <div style="font-size: 14px; color: #666;">{row['institucion']} | Año: {row['anio']}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Cursos
            cursos_list = grupo['cursos_dictados'].dropna().unique()
            cursos_texto = " • ".join([str(c) for c in cursos_list]) if len(cursos_list) > 0 else "Sin cursos asignados"

            st.markdown(f"""
                    <div style="margin-top: 25px;">
                        <div class="header-label">Cursos Dictados</div>
                        <div class="curso-box">{cursos_texto}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No se encontró ningún docente con ese criterio.")
