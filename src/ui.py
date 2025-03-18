import streamlit as st

class UI:
    @staticmethod
    def sidebar():
        """Menú de navegación lateral"""

        with st.sidebar:
            st.image("assets/logo.png", width=200)
            st.title("📊 Menú")
            return st.radio("Seleccione un módulo:",
                            ["Inicio", "Muertes por Suicidio", "Lesiones autoinfligidas",
                             "Datos Demográficos", "Registros Estadísticos Mensuales"]) # "Carga de Datos" no incluida

    @staticmethod
    def user_tabs():
        """Tab para navegar por la aplicacion"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inicio", "Datos Demográficos", "Lesiones autoinfligidas",
                                                "Muertes por Suicidio", "Registros Estadísticos Mensuales"])
        with tab1:
            st.write("contenido tab 1")
        with tab2:
            st.write("contenido tab 2")
        with tab3:
            st.write("contenido tab 3")
        with tab4:
            st.write("contenido tab 4")
        with tab5:
            st.write("contenido tab 5")


    @staticmethod
    def show_kpis(kpis):
        """Muestra tarjetas con métricas clave"""
        col1, col2, col3 = st.columns(3)
        col1.metric(label="📌 Total Casos", value=kpis["total_casos"])
        # col2.metric(label="🔹 Intentos Registrados", value=kpis["intentos"])
        col3.metric(label="📉 Tendencia Último Año", value=f"{kpis['tendencia']}%")

    @staticmethod
    def show_footer():
        st.markdown("---")
        st.markdown("Diseñado por: **Álvaro Montiel** © 2025")
