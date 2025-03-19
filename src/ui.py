import streamlit as st

class UI:
    @staticmethod
    def sidebar():
        """Menú de navegación lateral"""

        with st.sidebar:
            st.image("assets/logo.png", width=200)
            st.title("📊 Menú")
            return st.radio("Seleccione un módulo:",
                            ["Inicio",
                             "Muertes por suicidio",
                             "Lesiones autoinfligidas",
                             "Análisis demográfico",
                             "Registros estadísticos mensuales",
                             "Análisis temporal",
                             "Análisis geográfico"]) # "Carga de Datos" no incluida

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
        st.markdown("SEREMI de salud, región de Antofagasta. Unidad de vigilancia de enfermedades no transmisibles,"
                    " cáncer y ambiente.")
        st.markdown("Diseñado por: **Álvaro Montiel** © 2025")

