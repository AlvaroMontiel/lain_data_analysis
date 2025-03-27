import streamlit as st
import pandas as pd
from src.data_loader import DataLoader
from src.data_cleaner import ApplyCleaners
import plotly.express as px

# Formato de la página
st.set_page_config(
    page_title="Lesiones Autoinfligidas",
    page_icon="🩹"
)

st.markdown("# Lesiones Autoinfligidas")
st.sidebar.header("Lesiones Autoinfligidas")
st.write(
    """Visualización de datos de lesiones autoinfligidas
    en Antofagasta. Los datos son provisorios y eventualmente
    podrían cambiar con el tiempo.
    """
)

# -------------------------------------------------------------
# Data Loading
# Cargar datos desde un archivo Excel
# -------------------------------------------------------------
ruta_excel = "data/reporte_formularios_250106_1122.xlsx"
hoja_excel = "reporte_formularios_250106_1122"

loader = DataLoader(file_path=ruta_excel, sheet_name=hoja_excel)
df_raw = loader.load_data()

# -------------------------------------------------------------
# ApplyCleaners on raw dataframe
# Aplicar limpieza de datos al DataFrame crudo
# ------------------------------------------------------------- 
cleaner = ApplyCleaners(df_raw)
df_clean = cleaner.apply_cleaners()

# -------------------------------------------------------------
# Data Analysis and Visualization
# -------------------------------------------------------------

try:
    # Obtén los valores únicos para cada filtro
    df_clean["Fecha del evento"] = pd.to_datetime(df_clean["Fecha del evento"], errors='coerce')
    years = sorted(df_clean["Fecha del evento"].dt.year.unique()) if "Fecha del evento" in df_clean.columns else []
    regions = sorted(df_clean["Region"].unique()) if "Region" in df_clean.columns else []
    communes = sorted(df_clean["Comuna"].unique()) if "Comuna" in df_clean.columns else []

    # Filtros integrados dentro de la página
    selected_years = st.multiselect(
        "Seleccionar Año de Notificación", 
        options=years, default=[2024]
        )
    selected_regions = st.multiselect(
        "Seleccionar Región", 
        options=regions, 
        default=['REGION DE ANTOFAGASTA']
        )
    selected_communes = st.multiselect(
        "Seleccionar Comuna", 
        options=communes, 
        default=communes
        )
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Aplicar filtros al DataFrame
df_filtered = df_clean.copy()
if "Fecha del evento" in df_filtered.columns and selected_years:
    df_filtered = df_filtered[df_filtered["Fecha del evento"].isin(selected_years)]
if "Region" in df_filtered.columns and selected_regions:
    df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]
if "Comuna" in df_filtered.columns and selected_communes:
    df_filtered = df_filtered[df_filtered["Comuna"].isin(selected_communes)]

# Transformar el DataFrame a formato ancho (pivotar)
if "Comuna" in df_filtered.columns and "Semana Epidemiologica" in df_filtered.columns:
    # Agrupar por Región y Semana Epidemiológica, y contar los registros
    pivot_data = df_filtered.groupby(["Comuna", "Semana Epidemiologica"]).size().reset_index(name="Notificaciones")

    # Pivotar el DataFrame para que las semanas sean columnas
    pivot_table = pivot_data.pivot(index="Comuna", columns="Semana Epidemiologica", values="Notificaciones").fillna(0)

    # Ordenar las columnas (semanas) de 1 a 52
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)

    # Mostrar la tabla en Streamlit
    st.markdown("## Tabla de Notificaciones por Comuna y Semana Epidemiológica")
    st.dataframe(pivot_table)

    # Crear un gráfico de área acumulativa para todas las regiones
    st.markdown("## Curva Epidémica por Comuna")
    pivot_table_reset = pivot_table.reset_index()  # Restablecer el índice para usarlo en Plotly
    pivot_table_long = pivot_table_reset.melt(id_vars="Comuna", var_name="Semana Epidemiologica", value_name="Notificaciones")

    fig = px.area(
        pivot_table_long,
        x="Semana Epidemiologica",
        y="Notificaciones",
        color="Comuna",
        title="Curva Epidémica por Comuna y Semana Epidemiológica",
        labels={"Semana Epidemiologica": "Semana Epidemiológica", "Notificaciones": "Cantidad de Notificaciones"},
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Las columnas 'Comuna' y 'Semana Epidemiologica' no se encuentran en el DataFrame.")