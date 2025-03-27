import streamlit as st
import pandas as pd
from src.data_loader import DataLoader
from src.data_cleaner import FilterData
from src.data_cleaner import IntegerCleaner
from src.data_cleaner import DateCleaner
from src.data_cleaner import DuplicateCleaner
# from src.data_cleaner import ApplyCleaners
import plotly.express as px

# Formato de la página
st.set_page_config(
    page_title="LAIN",
    page_icon="🩹"
)

st.markdown("# Vigilancia epidemiológica de lesiones autoinfligidas")
st.sidebar.header("Lesiones Autoinfligidas")
st.write(
    """
    Esta página presenta un análisis descriptivo de los datos de vigilancia epidemiológica
    relacionados con lesiones autoinfligidas en la región de Antofagasta.
    
    Los datos son preliminares y están sujetos a actualizaciones futuras.
    
    Utilice los filtros disponibles para explorar la información por año,
    región y comuna, y visualice las tendencias a través de tablas y gráficos.
    """
)

# -------------------------------------------------------------
# Data Loading
# Cargar datos desde un archivo Excel
# -------------------------------------------------------------
ruta_excel = "data/reporte_formularios_250326_1946.xlsx"
hoja_excel = "reporte_formularios_250326_1946"

loader = DataLoader(file_path=ruta_excel, sheet_name=hoja_excel)
df_raw = loader.load_data()

# -------------------------------------------------------------
# ApplyCleaners on raw dataframe
# Aplicar limpieza de datos al DataFrame crudo
# ------------------------------------------------------------- 
st.markdown("## Limpieza de datos en proceso")
progress_text = st.empty()
progress_bar = st.progress(0)

with st.spinner("Iniciando limpieza de datos..."):
    # Etapa 1: Filtrar datos
    progress_text.text("Filtrando datos...")
    clean_data = FilterData(df_raw)
    df_clean = clean_data.get_filter_data()    
    progress_bar.progress(25)
    
    # Etapa 2: Limpiar columnas de fecha
    progress_text.text("Limpiando columnas de fecha...")
    clean_data = DateCleaner(df_clean)
    df_clean = clean_data.get_date_cleaned_data()
    progress_bar.progress(50)
    
    # Etapa 3: Limpiar columnas numéricas y de identificación
    progress_text.text("Limpiando columnas numéricas y de identificación...")
    clean_data = IntegerCleaner(df_clean)
    df_clean = clean_data.get_integer_cleaned_data()
    progress_bar.progress(75)
    
    # Etapa 4: Eliminar duplicados y ajustes finales
    progress_text.text("Eliminando duplicados y finalizando ajustes...")
    clean_data = DuplicateCleaner(df_clean)
    df_clean = clean_data.get_duplicate_cleaned_data()
    progress_bar.progress(100)
    
    progress_text.text("Limpieza completada!")

# -------------------------------------------------------------
# Data Analysis and Visualization
# -------------------------------------------------------------

try:
    # Obtener los valores únicos para cada filtro
    df_clean["Fecha del evento"] = pd.to_datetime(df_clean["Fecha del evento"], errors='coerce')
    years = sorted(
        df_clean["Fecha del evento"].dt.year.dropna().unique()) if "Fecha del evento" in df_clean.columns else []
    regions = sorted(df_clean["Region"].unique()) if "Region" in df_clean.columns else []
    communes = sorted(df_clean["Comuna"].unique()) if "Comuna" in df_clean.columns else []
    establecimientos = sorted(df_clean["Establecimiento Salud"].unique()) if "Establecimiento Salud" in df_clean.columns else []

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
    selected_communes = st.sidebar.multiselect(
        "Seleccionar Comuna", 
        options=communes, 
        default=communes
        )
    selected_establecimientos = st.sidebar.multiselect(
        "Seleccionar Establecimiento de Salud", 
        options=establecimientos, 
        default=['Hospital Dr. Leonardo Guzmán (Antofagasta)', 
                 'Hospital Dr. Carlos Cisternas (Calama)']
        )
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Aplicar filtros al DataFrame
df_filtered = df_clean.copy()
if "Fecha del evento" in df_filtered.columns and selected_years:
    df_filtered["Fecha del evento"] = pd.to_datetime(df_filtered["Fecha del evento"], errors="coerce")
    df_filtered = df_filtered[df_filtered["Fecha del evento"].dt.year.isin(selected_years)]
if "Region" in df_filtered.columns and selected_regions:
    df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]
if "Comuna" in df_filtered.columns and selected_communes:
    df_filtered = df_filtered[df_filtered["Comuna"].isin(selected_communes)]
if "Establecimiento Salud" in df_filtered.columns and selected_establecimientos:
    df_filtered = df_filtered[df_filtered["Establecimiento Salud"].isin(selected_establecimientos)]

# Transformar el DataFrame a formato ancho (pivotar)
if "Comuna" in df_filtered.columns and "Semana Epidemiologica" in df_filtered.columns:
    # Agrupar por Comuna y Semana Epidemiológica, y contar los registros
    pivot_data = df_filtered.groupby(["Comuna", "Semana Epidemiologica"]).size().reset_index(name="Notificaciones")

    # Pivotar el DataFrame para que las semanas sean columnas
    pivot_table = pivot_data.pivot(index="Comuna", columns="Semana Epidemiologica", values="Notificaciones").fillna(0)

    # Ordenar las columnas (semanas) de 1 a 52
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)

    # Mostrar la tabla en Streamlit
    st.markdown("## Tabla de Notificaciones por comuna y semana epidemiológica")
    st.dataframe(pivot_table)

   # Crear un gráfico de barras apiladas para todas las comunas
    st.markdown("## Curva epidemiológica por comuna (Barras apiladas)")
    pivot_table_reset = pivot_table.reset_index()  # Restablecer el índice para usarlo en Plotly
    pivot_table_long = pivot_table_reset.melt(id_vars="Comuna", var_name="Semana Epidemiologica", value_name="Notificaciones")

    fig = px.bar(
        pivot_table_long,
        x="Semana epidemiológica",
        y="Notificaciones",
        color="Comuna",
        title="Curva epidemiológica por comuna y semana epidemiológica",
        labels={"Semana Epidemiologica": "Semana Epidemiológica", "Notificaciones": "Número de Notificaciones"},
        template="plotly_dark",
        barmode="stack"  # Configuración para apilar las barras
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Las columnas 'Comuna' y 'Semana Epidemiologica' no se encuentran en el DataFrame.")

# -------------------------------------------------------------
# Histograma de la Edad de los Pacientes
# -------------------------------------------------------------
if "Edad Calculada" in df_filtered.columns:
    st.markdown("## Histograma de la Edad de los Pacientes")
    fig_age = px.histogram(
        df_filtered,
        x="Edad",
        nbins=20,
        title="Distribución de la Edad de los Pacientes",
        labels={"Edad": "Edad"}
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

    st.markdown("## Estadísticas Descriptivas de la Edad de los Pacientes")
    st.dataframe(descriptive_stats)
else:
    st.write("La columna 'Edad Calculada' no se encuentra en el DataFrame.")



