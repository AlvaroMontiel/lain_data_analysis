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

    # Menú
    selected_option = UI.sidebar()
    # selected_option = UI.user_tabs()

    # ✅ ACTUALIZACIÓN DEL NOMBRE DEL ARCHIVO
    ruta_excel = "data/reporte_formularios_250212_1610.xlsx"
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

    if selected_option == "Inicio":
        UI.show_kpis(kpis)
        st.subheader("📊 Análisis General")
        fig_hist = Visualization.histogram(df_clean, "Edad Paciente")
        st.plotly_chart(fig_hist, use_container_width=True)

    elif selected_option == "Muertes por Suicidio":
        st.subheader("📌 Análisis de Muertes por Suicidio")
        st.dataframe(DataAnalyzer(df_clean).basic_stats(["Edad Paciente"]))

    elif selected_option == "Intentos de Suicidio":
        st.subheader("📌 Análisis de Intentos de Suicidio")
        st.dataframe(DataAnalyzer(df_clean).frequency_table("Sexo Paciente"))

    # Sin autenticacion por el momento
    # elif selected_option == "Carga de Datos":
    #     st.subheader("🔄 Cargar nuevos datos")
    #
    #     # Requiere autenticación solo en esta sección
    #     user_email = st.text_input("Ingrese su correo")
    #     if st.button("Iniciar sesión"):
    #         if check_access(user_email):
    #             st.success("Acceso concedido")
    #
    #             # Módulo de carga de archivos
    #             uploaded_file = st.file_uploader("Suba un archivo Excel o CSV", type=["csv", "xlsx"])
    #             if uploaded_file:
    #                 st.success("Archivo cargado correctamente")
    #         else:
    #             st.error("Acceso denegado. No tiene permisos para cargar datos.")

    # Footer
    UI.show_footer()

if __name__ == "__main__":
    main()
