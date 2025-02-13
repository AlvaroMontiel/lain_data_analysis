import streamlit as st
from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer

def main():
    """
    Función principal que orquesta la carga, limpieza y análisis de datos.
    """
    st.title("Vigilancia Epidemiológica de Lesiones Autoinfligidas")

    # 1. Cargar datos con DataLoader
    # ------------------------------------------------
    ruta_excel = "data/reporte_formularios_250212_1610.xlsx"
    hoja_excel = "reporte_formularios_250212_1610"
    loader = DataLoader(file_path=ruta_excel, sheet_name=hoja_excel)
    df_raw = loader.load_data()

    st.subheader("Datos crudos cargados")
    st.write(df_raw.head())
    st.write(f"Filas x Columnas: {df_raw.shape}")

    # 2. Limpiar datos con DataCleaner
    # ------------------------------------------------
    cleaner = DataCleaner(df_raw)

    # Seleccionar las variables que se ocuparan en el analisis
    cleaner.select_variables(cleaner.selected_variables)

    # Aplicar el filtro primario
    cleaner.primary_filter()

    # Obtener el DataFrame limpio
    df_clean = cleaner.get_clean_data()

    st.subheader("Datos tras limpieza")
    st.write(df_clean.head())
    st.write(f"Filas x Columnas: {df_clean.shape}")

    # 3. Analizar datos con DataAnalyzer
    # ------------------------------------------------
    analyzer = DataAnalyzer(df_clean)

    st.subheader("Estadísticas descriptivas de 'Edad Paciente'")
    stats_edad = analyzer.basic_stats(columns=["Edad Paciente"])
    st.dataframe(stats_edad)

    st.subheader("Frecuencia de 'Sexo Paciente'")
    freq_sexo = analyzer.frequency_table("Sexo Paciente", normalize=True)
    st.dataframe(freq_sexo)

    st.subheader("Frecuencia de 'Orientación Sexual'")
    freq_orientacion_sexual = analyzer.frequency_table("Orientacion Sexual", normalize=True)
    st.dataframe(freq_orientacion_sexual)

    st.subheader("Frecuencia de 'Nacionalidad Paciente'")
    freq_nacionalidad = analyzer.frequency_table("Nacionalidad Paciente", normalize=True)
    st.dataframe(freq_nacionalidad)

    st.subheader("Histograma de 'Edad Paciente'")
    fig_hist = analyzer.histogram(column="Edad Paciente", nbins=15)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Boxplot de 'Edad Paciente' según 'Sexo Paciente'")
    fig_box = analyzer.boxplot(x_col="Sexo Paciente", y_col="Edad Paciente", color_col="Sexo Paciente")
    st.plotly_chart(fig_box, use_container_width=True)

if __name__ == "__main__":
    main()
