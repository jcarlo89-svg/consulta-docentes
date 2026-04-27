import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Consulta de Grados Académicos", layout="wide")

# Cargar o crear la base de datos
DB_FILE = 'docentes_v2.csv'
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=['dni', 'nombre', 'grado', 'institucion', 'anio'])
    df.to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE, dtype={'dni': str})

# --- INTERFAZ PÚBLICA (CONSULTA) ---
st.title("🏛️ Sistema de Consulta Universitaria")
st.markdown("Busca los grados y títulos registrados de los docentes.")

busqueda = st.text_input("Ingrese DNI o Apellidos del docente:")

if busqueda:
    # Filtrar datos
    resultado = df[(df['dni'] == busqueda) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not resultado.empty:
        for _, row in resultado.iterrows():
            # Crear el diseño tipo SUNEDU con columnas
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1.5])
                with col1:
                    st.markdown(f"**GRADUADO**\n\n{row['nombre']}\n\nDNI {row['dni']}")
                with col2:
                    st.markdown(f"**GRADO O TÍTULO**\n\n<span style='color:#00B5E2; font-weight:bold;'>{row['grado']}</span>", unsafe_allow_html=True)
                    st.caption(f"Año de diploma: {row['anio']}")
                with col3:
                    st.markdown(f"**INSTITUCIÓN**\n\n{row['institucion']}")
                st.divider()
    else:
        st.error("No se encontraron registros coincidentes.")

# --- PANEL DE ADMINISTRACIÓN (ALIMENTAR BASE DE DATOS) ---
st.sidebar.title("Administración")
password = st.sidebar.text_input("Contraseña para editar", type="password")

if password == "admin123": # Cambia esta contraseña
    st.sidebar.success("Acceso concedido")
    st.header("⚙️ Panel de Gestión de Datos")
    
    with st.expander("Añadir Nuevo Grado"):
        with st.form("nuevo_registro"):
            dni_n = st.text_input("DNI")
            nom_n = st.text_input("Nombre Completo")
            gra_n = st.text_input("Grado o Título")
            ins_n = st.text_input("Institución")
            ani_n = st.text_input("Año")
            
            if st.form_submit_button("Guardar Registro"):
                nuevo_df = pd.DataFrame([[dni_n, nom_n, gra_n, ins_n, ani_n]], columns=df.columns)
                df = pd.concat([df, nuevo_df], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("¡Registro guardado! Recarga la página.")

    st.write("### Base de datos actual")
    st.dataframe(df)