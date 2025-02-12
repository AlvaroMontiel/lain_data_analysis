from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer

def main():
    """
    Función principal que orquesta la carga, limpieza y análisis de datos.
    """

    # 1. Cargar datos con DataLoader
    # ------------------------------------------------
    ruta_excel = "data/reporte_formularios_250212_1610.xlsx"
    hoja_excel = "reporte_formularios_250212_1610"

    loader = DataLoader(file_path=ruta_excel, sheet_name=hoja_excel)
    df_raw = loader.load_data()

    print("\n--- [1] Datos crudos cargados ---")
    print(df_raw.head())
    print(f"Filas x Columnas: {df_raw.shape}\n")

    # 2. Limpiar datos con DataCleaner
    # ------------------------------------------------
    cleaner = DataCleaner(df_raw)

    # Seleccionar las variables que se ocuparan en el analisis
    cleaner.select_variables(cleaner.selected_variables)

    # Aplicar el filtro primario
    # cleaner.primary_filter()

    # Obtener el DataFrame limpio
    df_clean = cleaner.get_clean_data()

    print("\n--- [2] Datos tras limpieza ---")
    print(df_clean.head())
    print(f"Filas x Columnas: {df_clean.shape}\n")

    # 3. Analizar datos con DataAnalyzer
    # ------------------------------------------------
    analyzer = DataAnalyzer(df_clean)

    # 3.1 Ejemplo: estadísticas descriptivas de la columna 'Edad Paciente'
    stats_edad = analyzer.basic_stats(columns=["Edad Paciente"])
    print("--- [3.1] Estadísticas descriptivas de 'edad' ---")
    print(stats_edad, "\n")

    # 3.2 Ejemplo: tabla de frecuencias de la columna 'Sexo Paciente'
    freq_sexo = analyzer.frequency_table("Sexo Paciente", normalize=True)
    print("--- [3.2] Frecuencia de 'sexo' ---")
    print(freq_sexo, "\n")

    # 3.3 Ejemplo: generar un histograma de la edad
    # (en modo consola no lo verás, pero en un entorno interactivo sí)
    fig_hist = analyzer.histogram(column="Edad Paciente", nbins=10)
    # Si estuvieras en un notebook o en Streamlit, podrías mostrarlo así:
    # st.plotly_chart(fig_hist)

    # 3.4 Ejemplo: boxplot de 'edad' según 'sexo'
    fig_box = analyzer.boxplot(x_col="Sexo Paciente", y_col="Edad Paciente", color_col="Sexo Paciente")
    # Ídem: en un entorno interactivo, se visualizaría:
    # st.plotly_chart(fig_box)

    print("--- [3.3 y 3.4] Gráficos generados (plotly Figures) ---")
    print("Usar en un entorno interactivo como Jupyter/Streamlit/Dash para verlos.\n")

    print("Finalizado el flujo de orquestación de datos.")


if __name__ == "__main__":
    main()
