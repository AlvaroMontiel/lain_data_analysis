import streamlit as st
from src.ui import UI
from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer
from src.visualization import Visualization
# from src.auth import check_access


def main():
    st.set_page_config(page_title="Vigilancia Epidemiológica", layout="wide")
    st.title("🔍 Vigilancia Epidemiológica de Lesiones Autoinfligidas y Muertes por Suicidio")

    # Menú, usa radio
    selected_option = UI.sidebar()

    # ✅ NOMBRE DEL ARCHIVO
    ruta_excel = "/home/alvaro/PycharmProjects/lain_data_analysis/data/reporte_formularios_250212_1610.xlsx"
    hoja_excel = "reporte_formularios_250212_1610"

    loader = DataLoader(file_path=ruta_excel, sheet_name=hoja_excel)
    df_raw = loader.load_data()

    # Limpieza de datos
    cleaner = DataCleaner(df_raw)
    cleaner.primary_filter()
    df_clean = cleaner.get_clean_data()

    # Módulo de KPIs
    kpis = {
        "total_casos": df_clean.shape[0],
       # "intentos": df_clean["Tipo Evento"].value_counts().get("Intento de Suicidio", 0),
        "tendencia": round((df_clean.shape[0] - 500) / 500 * 100, 2)  # Ejemplo de cálculo
    }

    # Navegación según la opción elegida en el sidebar
    if selected_option == "Inicio":
        st.subheader("📊 Análisis General (Placeholder)")
        st.info("Aquí irá un resumen general de los datos. Gráficos, tablas, etc.")
        UI.show_kpis(kpis)
        fig_hist = Visualization.histogram(df_clean, "Edad Paciente")
        st.plotly_chart(fig_hist, use_container_width=True)

    elif selected_option == "Muertes por suicidio":
        st.subheader("📌 Análisis de muertes por suicidio")
        st.info("Placeholder donde se mostrarán estadísticas específicas de muertes por suicidio.")
        # st.dataframe(DataAnalyzer(df_clean).basic_stats(["Edad Paciente"]))
        st.write("Placeholder: Analisis de las muertes por suicidio")

    elif selected_option == "Lesiones autoinfligidas":
        st.subheader("📌 Análisis de lesiones autoinfligidas")
        st.info("Placeholder para mostrar frecuencias, perfiles y correlaciones de intentos de suicidio.")
        st.write("Placeholder: Analisis de las lesiones autoinfligidas")
        # st.dataframe(DataAnalyzer(df_clean).frequency_table("Sexo Paciente"))

    elif selected_option == "Análisis demográfico":
        st.subheader("📌 Análisis demográfico")
        st.info("Aquí irá el análisis demográfico. Estadísticas por sexo, edad, etc.")
        # Placeholder simple
        st.write("Placeholder: Gráficos de pirámides poblacionales, distribuciones, etc.")

    elif selected_option == "Regristros estadísticos mensuales":
        st.subheader("📌 Regristros estadísticos mensuales")
        st.info("Placeholder para análisis de los REM.")
        # Placeholder
        st.write("Placeholder: Gráficos sobre REMs.")

    elif selected_option == "Análisis temporal":
        st.subheader("📌 Análisis temporal")
        st.info("Placeholder para tendencias y evoluciones de eventos a lo largo del tiempo.")
        # Placeholder
        st.write("Placeholder: Series de tiempo, tendencias mensuales/anuales...")

    elif selected_option == "Análisis geográfico":
        st.subheader("📌 Análisis geográfico")
        st.info("Placeholder para mapas y análisis geoespacial.")
        # Placeholder
        st.write("Placeholder: Mapas de calor, coropletas, etc.")

    # Footer
    UI.show_footer()

if __name__ == "__main__":
    main()
