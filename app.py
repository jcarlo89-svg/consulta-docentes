import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="Consulta de Grados", layout="wide")

st.title("🏛️ Sistema de Consulta Universitaria")

# Conexión a Google Sheets
# Nota: La URL se configurará en el paso 3 en Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer los datos
try:
    df = conn.read()
except Exception as e:
    st.error("Error al conectar con la base de datos. Verifica la configuración.")
    df = pd.DataFrame()

# --- BUSCADOR ---
busqueda = st.text_input("Ingrese DNI o Apellidos del docente:")

if busqueda and not df.empty:
    resultado = df[(df['dni'].astype(str) == busqueda) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not resultado.empty:
        for _, row in resultado.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1.5])
                with col1:
                    st.markdown(f"**GRADUADO**\n\n{row['nombre']}\n\nDNI {row['dni']}")
                with col2:
                    st.markdown(f"**GRADO O TÍTULO**\n\n<span style='color:#00B5E2; font-weight:bold;'>{row['grado']}</span>", unsafe_allow_html=True)
                    st.caption(f"Año: {row['anio']}")
                with col3:
                    st.markdown(f"**INSTITUCIÓN**\n\n{row['institucion']}")
                st.divider()
    else:
        st.warning("No se encontraron registros.")

# --- PANEL ADMIN PARA ALIMENTAR ---
st.sidebar.title("Administración")
if st.sidebar.text_input("Contraseña", type="password") == "admin123":
    st.sidebar.success("Acceso concedido")
    with st.sidebar.form("Añadir Registro"):
        dni = st.text_input("DNI")
        nombre = st.text_input("Nombre Completo")
        grado = st.text_input("Grado")
        inst = st.text_input("Institución")
        anio = st.text_input("Año")
        
        if st.form_submit_button("Guardar en Google Sheets"):
            # Crear nueva fila
            nueva_fila = pd.DataFrame([[dni, nombre, grado, inst, anio]], columns=df.columns)
            actualizado = pd.concat([df, nueva_fila], ignore_index=True)
            # Guardar de vuelta en Google Sheets
            conn.update(data=actualizado)
            st.sidebar.success("¡Datos guardados permanentemente!")
            st.rerun()
