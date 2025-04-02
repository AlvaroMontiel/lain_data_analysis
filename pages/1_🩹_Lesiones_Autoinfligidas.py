import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import DataLoader

# Formato de la página
st.set_page_config(
    page_title="LAIN",
    page_icon="🩹"
)

st.sidebar.image("assets/logo.png", width=200)

st.markdown("# Vigilancia epidemiológica de lesiones autoinfligidas")
st.sidebar.header("Lesiones Autoinfligidas")
st.markdown(
    """
    ---
    ## Introducción
    Esta página presenta un análisis descriptivo de los datos de vigilancia epidemiológica
    de lesiones autoinfligidas en la región de Antofagasta.
    
    **Los datos son preliminares y están sujetos a actualizaciones futuras.**

    ## Instrucciones
    Utilice los filtros disponibles en la **barra lateral izquierda** para explorar la información por año,
    región, comuna, sexo, subclasificación y establecimiento de salud donde se notifique el evento. 
    
    Asegúrese de **seleccionar al menos** un año y una región para obtener resultados significativos.
    Los gráficos y tablas se **actualizarán automáticamente** según los filtros seleccionados.
    Si no se selecciona ningún filtro, se mostrarán todos los datos disponibles.

    --- 
    """
)

# -------------------------------------------------------------
# Data Loading
# Cargar datos desde un archivo Excel
# -------------------------------------------------------------
ruta_excel = "data/set_datos_lain_para_analisis.xlsx"
hoja_excel = "Sheet1" 

loader = DataLoader(file_path=ruta_excel, sheet_name=hoja_excel)
df_clean = loader.load_data()

# -------------------------------------------------------------
# Data Analysis and Visualization
# -------------------------------------------------------------

st.markdown("# Análisis por región")

try:
    # Obtener los valores únicos para cada filtro
    df_clean["Fecha del evento"] = pd.to_datetime(df_clean["Fecha del evento"], errors='coerce')
    years = sorted(
        df_clean["Fecha del evento"].dt.year.dropna().unique()) if "Fecha del evento" in df_clean.columns else []
    regions = sorted(df_clean["Region"].unique()) if "Region" in df_clean.columns else []
    communes = sorted(df_clean["Comuna"].unique()) if "Comuna" in df_clean.columns else []
    genre = sorted(df_clean["Sexo Paciente"].unique()) if "Sexo Paciente" in df_clean.columns else []
    mental_health_record = sorted(df_clean["Tiene Antecedentes salud mental"].unique()) if "Tiene Antecedentes salud mental" in df_clean.columns else []

    # Filtros integrados dentro de la página
    selected_years = st.sidebar.multiselect(
        "Seleccionar Año de Notificación", 
        options=years, default=[2024]
        )
    selected_regions = st.sidebar.multiselect(
        "Seleccionar Región", 
        options=regions, 
        default=['REGION DE ANTOFAGASTA']
        )
    selected_genres = st.sidebar.multiselect(
        "Seleccionar Sexo", 
        options=genre, 
        default=genre
        )
    selected_sub_clasification = st.sidebar.multiselect(
        "Seleccionar Sub Clasificación", 
        options=df_clean["Subclasificacion"].unique(), 
        default=df_clean["Subclasificacion"].unique()
        )
    selected_mental_health_record = st.sidebar.multiselect(
        "Antecedentes de Salud Mental", 
        options=mental_health_record, 
        default=mental_health_record
        )
    # selected_event_place = st.sidebar.multiselect(
    #     "Lugar del evento", 
    #     options=df_clean["Lugar del evento"].unique(), 
    #     default=df_clean["Lugar del evento"].unique()
    #     )

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Filtrar establecimientos a partir de las regiones seleccionadas
if selected_regions:
    df_region = df_clean[df_clean["Region"].isin(selected_regions)]
    establecimientos = sorted(df_region["Establecimiento Salud"].unique()) if "Establecimiento Salud" in df_clean.columns else []
else:
    establecimientos = sorted(df_clean["Establecimiento Salud"].unique()) if "Establecimiento Salud" in df_clean.columns else []

selected_establecimientos = st.sidebar.multiselect(
    "Seleccionar Establecimiento de Salud", 
    options=establecimientos, 
    default=[]
)

# Filtrar Nacionalidad disponibles según la región seleccionada
if selected_regions:
    df_region = df_clean[df_clean["Region"].isin(selected_regions)]
    nacionality = sorted(df_region["Nacionalidad Paciente"].unique()) if "Nacionalidad Paciente" in df_clean.columns else []
else:
    nacionality = sorted(df_clean["Nacionalidad Paciente"].unique()) if "Nacionalidad Paciente" in df_clean.columns else []

selected_nacionality = st.sidebar.multiselect(
    "Nacionalidad", 
    options=nacionality, 
    default=[]
)

# Aplicar filtros al DataFrame
# Aplicar filtros al DataFrame
df_filtered = df_clean.copy()
if "Fecha del evento" in df_filtered.columns and selected_years:
    df_filtered["Fecha del evento"] = pd.to_datetime(df_filtered["Fecha del evento"], errors="coerce")
    df_filtered = df_filtered[df_filtered["Fecha del evento"].dt.year.isin(selected_years)]
if "Region" in df_filtered.columns and selected_regions:
    df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]
if "Establecimiento Salud" in df_filtered.columns and selected_establecimientos:
    df_filtered = df_filtered[df_filtered["Establecimiento Salud"].isin(selected_establecimientos)]
if "Nacionalidad Paciente" in df_filtered.columns and selected_nacionality:
    df_filtered = df_filtered[df_filtered["Nacionalidad Paciente"].isin(selected_nacionality)]
if "Sexo Paciente" in df_filtered.columns and selected_genres:
    df_filtered = df_filtered[df_filtered["Sexo Paciente"].isin(selected_genres)]
if "Subclasificacion" in df_filtered.columns and selected_sub_clasification:  
    df_filtered = df_filtered[df_filtered["Subclasificacion"].isin(selected_sub_clasification)]
if "Tiene Antecedentes salud mental" in df_filtered.columns and selected_mental_health_record:
    df_filtered = df_filtered[df_filtered["Tiene Antecedentes salud mental"].isin(selected_mental_health_record)]

# if "Lugar del evento" in df_filtered.columns and selected_event_place:
#     df_filtered = df_filtered[df_filtered["Lugar del evento"].isin(selected_event_place)]


# -------------------------------------------------------------
# Tabla resumen: Total de casos y porcentaje según región
# -------------------------------------------------------------

# Tabla resumen: Total de casos y porcentaje según subclasificación
if "Subclasificacion" in df_filtered.columns:
    # Calcular el total de casos por subclasificación
    subclas_counts = df_filtered["Subclasificacion"].value_counts().reset_index()
    subclas_counts.columns = ["Subclasificacion", "Total Casos"]
    total_casos = subclas_counts["Total Casos"].sum()
    # Calcular porcentaje y redondear a 2 decimales
    subclas_counts["Porcentaje (%)"] = (subclas_counts["Total Casos"] / total_casos * 100).round(2)
    
    # Crear una fila con el total general
    total_row = pd.DataFrame({
        "Subclasificacion": ["TOTAL"],
        "Total Casos": [total_casos],
        "Porcentaje (%)": [100.00]
    })
    
    # Concatenar la fila total al DataFrame original
    subclas_counts = pd.concat([subclas_counts, total_row], ignore_index=True)
    
    st.markdown("## Número de eventos y porcentaje según subclasificación")
    st.dataframe(subclas_counts)
else:
    st.write("La columna 'Subclasificacion' no se encuentra en el DataFrame.")

# Análisis de la Subclasificación para intencionalidad suicida
if "Subclasificacion" in df_filtered.columns:
    st.markdown("## Distribución de la intención suicida según subclasificación")
    subclas_counts = df_filtered["Subclasificacion"].value_counts().reset_index()
    subclas_counts.columns = ["Subclasificacion", "Notificaciones"]
    fig_subclas = px.bar(
        subclas_counts,
        x="Subclasificacion",
        y="Notificaciones",
        title="Eventos según intención suicida",
        labels={"Subclasificacion": "Subclasificación", "Notificaciones": "Número de Notificaciones"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_subclas, use_container_width=True)
else:
    st.write("La columna 'Subclasificacion' no se encuentra en el DataFrame.")

# -------------------------------------------------------------
# Curva epidemiológica por región y semana epidemiológica
# -------------------------------------------------------------

# Transformar el DataFrame a formato ancho (pivotar)
if "Region" in df_filtered.columns and "Semana Epidemiologica" in df_filtered.columns:
    # Agrupar por Region y Semana Epidemiológica, y contar los registros
    pivot_data = df_filtered.groupby(["Region", "Semana Epidemiologica"]).size().reset_index(name="Notificaciones")

    # Pivotar el DataFrame para que las semanas sean columnas
    pivot_table = pivot_data.pivot(index="Region", columns="Semana Epidemiologica", values="Notificaciones").fillna(0)

    # Ordenar las columnas (semanas) de 1 a 52
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)

    # Convertir las columnas a enteros
    pivot_table.columns = pivot_table.columns.astype(int)
    pivot_table.columns.name = "Semana Epidemiologica"

    # Mostrar la tabla en Streamlit
    st.markdown("## Número de eventos por región y semana epidemiológica")
    st.dataframe(pivot_table)

   # Crear un gráfico de barras apiladas para todas las comunas
    st.markdown("## Curva epidemiológica según región y semana epidemiológica (Barras apiladas)")
    pivot_table_reset = pivot_table.reset_index()  # Restablecer el índice para usarlo en Plotly
    pivot_table_long = pivot_table_reset.melt(id_vars="Region", var_name="Semana Epidemiologica", value_name="Notificaciones")

    fig = px.bar(
        pivot_table_long,
        x="Semana Epidemiologica",
        y="Notificaciones",
        color="Region",
        title="Curva epidemiológica por región y semana epidemiológica",
        labels={"Semana Epidemiologica": "Semana Epidemiológica", "Notificaciones": "Número de Notificaciones"},
        template="plotly_dark",
        barmode="stack"  # Configuración para apilar las barras
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Las columnas 'Region' y 'Semana Epidemiologica' no se encuentran en el DataFrame.")

# -------------------------------------------------------------
# Histograma de la Edad de los Pacientes
# -------------------------------------------------------------
if "Edad Calculada" in df_filtered.columns:
    st.markdown("## Distribución por edad: Perfil etario de lesiones autoinfligidas")
    fig_age = px.histogram(
        df_filtered,
        x="Edad Calculada",
        nbins=20,
        title="Distribución de la edad de los pacientes",
        labels={"Edad Calculada": "Edad"}
    )
    st.plotly_chart(fig_age, use_container_width=True)
else:
    st.write("La columna 'Edad Calculada' no se encuentra en el DataFrame.")

# -------------------------------------------------------------
# Tabla descriptiva de la Edad de los Pacientes
# -------------------------------------------------------------

if "Edad Calculada" in df_filtered.columns:
    edad = df_filtered["Edad Calculada"]
    minEdad = edad.min()
    maxEdad = edad.max()
    meanEdad = edad.mean()
    medianEdad = edad.median()
    stdEdad = edad.std()
    cvEdad = stdEdad / meanEdad if meanEdad != 0 else None

    # Creamos un DataFrame con los estadísticos descriptivos
    descriptive_stats = pd.DataFrame({
        "Mínimo": [minEdad],
        "Máximo": [maxEdad],
        "Media": [meanEdad],
        "Mediana": [medianEdad],
        "Desviación Estándar": [stdEdad],
        "Coeficiente de Variación": [cvEdad]
    })

    st.markdown("## Estadísticas descriptivas de la edad de los pacientes")
    st.dataframe(descriptive_stats)
else:
    st.write("La columna 'Edad Calculada' no se encuentra en el DataFrame.")

# Boxplot de distribución de edades según sexo
if "Edad Calculada" in df_filtered.columns and "Sexo Paciente" in df_filtered.columns:
    st.markdown("## Distribución de la edad según sexo")
    fig_box = px.box(
        df_filtered,
        x="Sexo Paciente",
        y="Edad Calculada",
        title="Boxplot de edad por sexo",
        labels={"Sexo Paciente": "Sexo", "Edad Calculada": "Edad"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.write("Las columnas 'Edad Calculada' o 'Region' no se encuentran en el DataFrame.")


# Boxplot de distribución de edades según metodo de autolesión
if "Edad Calculada" in df_filtered.columns and "Metodo de Lesion" in df_filtered.columns:
    st.markdown("## Distribución de la edad según método de autolesión")
    fig_box = px.box(
        df_filtered,
        x="Metodo de Lesion",
        y="Edad Calculada",
        title="Boxplot de edad por metodo de autolesión",
        labels={"Metodo de Lesion": "Método de autolesión", "Edad Calculada": "Edad"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.write("Las columnas 'Edad Calculada' o 'Region' no se encuentran en el DataFrame.")


# -------------------------------------------------------------
# Filtro adicional para Comunas (análisis independiente)
# -------------------------------------------------------------

st.markdown("# Análisis por comuna") 

# Filtrar comunas disponibles según la región seleccionada
if selected_regions:
    available_communes = sorted(df_clean[df_clean["Region"].isin(selected_regions)]["Comuna"].unique())
else:
    available_communes = sorted(df_clean["Comuna"].unique()) if "Comuna" in df_clean.columns else []

if "Comuna" in df_clean.columns:
    # Usamos un key único para evitar duplicados con otros multiselect
    selected_communes = st.sidebar.multiselect(
        "Seleccionar Comuna", 
        options=available_communes, 
        default=available_communes,
        key="selected_communes_by_region"
    )
else:
    selected_communes = []

# Sección de análisis por Comunas (solo si se han seleccionado comunas)
if "Comuna" in df_filtered.columns and selected_communes:
    df_commune = df_filtered[df_filtered["Comuna"].isin(selected_communes)]
    # Análisis 0: Tabla resumen de total de casos y porcentaje según comuna según subclasificación
    if "Subclasificacion" in df_commune.columns:
        # Tabla resumen: Total de casos y porcentaje según subclasificación
    # Calcular el total de casos por subclasificación
        subclas_counts = df_commune["Subclasificacion"].value_counts().reset_index()
        subclas_counts.columns = ["Subclasificacion", "Total Casos"]
        total_casos = subclas_counts["Total Casos"].sum()
        # Calcular porcentaje y redondear a 2 decimales
        subclas_counts["Porcentaje (%)"] = (subclas_counts["Total Casos"] / total_casos * 100).round(2)
        
        # Crear una fila con el total general
        total_row = pd.DataFrame({
            "Subclasificacion": ["TOTAL"],
            "Total Casos": [total_casos],
            "Porcentaje (%)": [100.00]
        })
        
        # Concatenar la fila total al DataFrame original
        subclas_counts = pd.concat([subclas_counts, total_row], ignore_index=True)
        
        st.markdown("## Número de eventos y porcentaje según subclasificación")
        st.dataframe(subclas_counts)
    else:
        st.write("La columna 'Subclasificacion' no se encuentra en el DataFrame.")



    
    # Análisis 1: Tabla y gráfica de notificaciones por comuna y semana epidemiológica
    if "Semana Epidemiologica" in df_commune.columns:
        pivot_data_comm = df_commune.groupby(["Comuna", "Semana Epidemiologica"]).size().reset_index(name="Notificaciones")
        
        # Pivotar el DataFrame
        pivot_table_comm = pivot_data_comm.pivot(index="Comuna", columns="Semana Epidemiologica", values="Notificaciones").fillna(0)
        pivot_table_comm = pivot_table_comm.reindex(sorted(pivot_table_comm.columns), axis=1)
        pivot_table_comm.columns = pivot_table_comm.columns.astype(int)
        pivot_table_comm.columns.name = "Semana Epidemiologica"
        
        st.markdown("### Número de eventos por comuna y semana epidemiológica")
        st.dataframe(pivot_table_comm)
        
        st.markdown("### Curva epidemiológica por comuna (Barras apiladas)")
        pivot_table_comm_reset = pivot_table_comm.reset_index()
        pivot_table_comm_long = pivot_table_comm_reset.melt(id_vars="Comuna", var_name="Semana Epidemiologica", value_name="Notificaciones")
        
        fig_comm = px.bar(
            pivot_table_comm_long,
            x="Semana Epidemiologica",
            y="Notificaciones",
            color="Comuna",
            title="Curva epidemiológica por comuna y semana epidemiológica",
            labels={"Semana Epidemiologica": "Semana Epidemiológica", "Notificaciones": "Número de Notificaciones"},
            template="plotly_dark",
            barmode="stack"
        )
        st.plotly_chart(fig_comm, use_container_width=True, key="plotly_chart_comm_curve")
    else:
        st.write("La columna 'Semana Epidemiologica' no se encuentra en los datos por comuna.")
    
    # Análisis 2: Histograma de edad para cada comuna (opcional)
    if "Edad Calculada" in df_commune.columns:
        st.markdown("### Distribución de la edad por comuna")
        fig_age_comm = px.histogram(
            df_commune,
            x="Edad Calculada",
            nbins=20,
            color="Comuna",
            title="Histograma de edad por comuna",
            labels={"Edad Calculada": "Edad"}
        )
        st.plotly_chart(fig_age_comm, use_container_width=True, key="plotly_chart_comm_age")
    else:
        st.write("La columna 'Edad Calculada' no se encuentra en los datos por comuna.")
    
    # -------------------------------------------------------------
    # Tabla descriptiva de la Edad de los Pacientes por Comuna
    # -------------------------------------------------------------
    if "Edad Calculada" in df_commune.columns:
        edad = df_commune["Edad Calculada"]
        minEdad = edad.min()
        maxEdad = edad.max()
        meanEdad = edad.mean()
        medianEdad = edad.median()
        stdEdad = edad.std()
        cvEdad = stdEdad / meanEdad if meanEdad != 0 else None

        # Creamos un DataFrame con los estadísticos descriptivos
        descriptive_stats = pd.DataFrame({
            "Mínimo": [minEdad],
            "Máximo": [maxEdad],
            "Media": [meanEdad],
            "Mediana": [medianEdad],
            "Desviación Estándar": [stdEdad],
            "Coeficiente de Variación": [cvEdad]
        })

        st.markdown("## Estadísticas descriptivas de la edad de los pacientes por comuna")
        st.dataframe(descriptive_stats)
    else:
        st.write("La columna 'Edad Calculada' no se encuentra en los datos por comuna.")

    # Boxplot de distribución de edades según sexo
    if "Edad Calculada" in df_commune.columns and "Sexo Paciente" in df_commune.columns:
        st.markdown("## Distribución de la edad según sexo por comuna")
        fig_box = px.box(
            df_commune,
            x="Sexo Paciente",
            y="Edad Calculada",
            title="Boxplot de edad por sexo",
            labels={"Sexo Paciente": "Sexo", "Edad Calculada": "Edad"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_box, use_container_width=True, key="plotly_chart_box_sexo")
    else:
        st.write("Las columnas 'Edad Calculada' o 'Sexo Paciente' no se encuentran en los datos por comuna.")

    # Boxplot de distribución de edades según método de autolesión
    if "Edad Calculada" in df_commune.columns and "Metodo de Lesion" in df_commune.columns:
        st.markdown("## Distribución de la edad según método de autolesión por comuna")
        fig_box = px.box(
            df_commune,
            x="Metodo de Lesion",
            y="Edad Calculada",
            title="Boxplot de edad por método de autolesión",
            labels={"Metodo de Lesion": "Método de autolesión", "Edad Calculada": "Edad"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_box, use_container_width=True, key="plotly_chart_box_metodo")
    else:
        st.write("Las columnas 'Edad Calculada' o 'Metodo de Lesion' no se encuentran en los datos por comuna.")
else:
    st.info("No se han seleccionado comunas.")

st.markdown(
    """
    # Análisis Consolidados
    ## Nacionalidad, orientación sexual e identidad de género según región y comuna
    """,
    unsafe_allow_html=True
)

# Gráfico Sunburst para la distribución de nacionalidad por región y comuna
if "Region" in df_filtered.columns and "Comuna" in df_filtered.columns and "Nacionalidad Paciente" in df_filtered.columns:
    fig_sunburst = px.sunburst(
        df_filtered,
        path=["Region", "Comuna", "Nacionalidad Paciente"],
        title="Distribución de Nacionalidad por Región y Comuna",
        template="plotly_dark"
    )
    st.plotly_chart(fig_sunburst, use_container_width=True, key="plotly_chart_sunburst")
else:
    st.write("No se encuentran las columnas necesarias para el gráfico Sunburst.")

# Gráfico Sunburst para la distribución de Orientación sexual por región y comuna
if "Region" in df_filtered.columns and "Comuna" in df_filtered.columns and "Orientacion Sexual" in df_filtered.columns:
    fig_sunburst = px.sunburst(
        df_filtered,
        path=["Region", "Comuna", "Orientacion Sexual"],
        title="Distribución de Orientación sexual por Región y Comuna",
        template="plotly_dark"
    )
    st.plotly_chart(fig_sunburst, use_container_width=True, key="plotly_chart_sunburst_orientacion")
else:
    st.write("No se encuentran las columnas necesarias para el gráfico Sunburst.")

# Gráfico Sunburst para la distribución de Identidad de género por región y comuna
if "Region" in df_filtered.columns and "Comuna" in df_filtered.columns and "Identidad de Genero" in df_filtered.columns:
    fig_sunburst = px.sunburst(
        df_filtered,
        path=["Region", "Comuna", "Identidad de Genero"],
        title="Distribución de la identidad de género por Región y Comuna",
        template="plotly_dark"
    )
    st.plotly_chart(fig_sunburst, use_container_width=True, key="plotly_chart_sunburst_genero")
else:
    st.write("No se encuentran las columnas necesarias para el gráfico Sunburst.")

# -------------------------------------------------------------
st.markdown(
    """
    <footer style="text-align: center; font-size: 22px; padding: 10px; margin-top: 50px; border-top: 1px solid #ccc;">
       <strong>Unidad de vigilancia epidemiológica de enfermedades no transmisibles, cáncer y ambiente</strong>
    </footer>
    """,
    unsafe_allow_html=True
)

