if busqueda:
    # Filtro de búsqueda
    res = df[(df['dni'].astype(str).str.contains(busqueda)) | (df['nombre'].str.contains(busqueda, case=False, na=False))]
    
    if not res.empty:
        for nombre, grupo in res.groupby('nombre'):
            dni_val = grupo['dni'].iloc[0]
            especialidad = str(grupo['especialidad'].iloc[0]) if 'especialidad' in grupo.columns and pd.notna(grupo['especialidad'].iloc[0]) else "No definida"
            cursos = str(grupo['cursos_dictados'].iloc[0]) if 'cursos_dictados' in grupo.columns and pd.notna(grupo['cursos_dictados'].iloc[0]) else "Sin cursos registrados"

            # 1. ENCABEZADO DE LA FICHA
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
                <div style="margin-top: 25px; border-top: 1px solid #eee; padding-top: 10px;">
                    <div class="header-label">Historial Académico</div>
                </div>
            """, unsafe_allow_html=True)

            # 2. LISTADO DE GRADOS (Uno por uno)
            for _, row in grupo.iterrows():
                st.markdown(f"""
                    <div class="grado-item">
                        <div class="grado-titulo">{row['grado']}</div>
                        <div class="grado-inst">{row['institucion']} | <b>Año: {row['anio']}</b></div>
                    </div>
                """, unsafe_allow_html=True)

            # 3. CIERRE DE FICHA Y CURSOS
            st.markdown(f"""
                <div style="margin-top: 20px;">
                    <div class="header-label">Cursos Dictados</div>
                    <div class="curso-box">{cursos}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("No se encontraron resultados.")
