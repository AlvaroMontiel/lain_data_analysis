import streamlit as st

st.set_page_config(
    page_title="Vigilancia epidemiológica de lesiones autoinfligidas y muertes por suicidio",
    page_icon="👋",
)

st.sidebar.image("/home/alvaro/PycharmProjects/lain_data_analysis/assets/logo.png", width=200)

st.write("# Bienvenido a la aplicación de vigilancia epidemiológica 👋")
st.write("Esta herramienta está diseñada para visualizar datos relacionados con "
        "lesiones autoinfligidas y muertes por suicidio.")

st.sidebar.success("Selecciona una de las secciones del menú para comenzar.")

st.markdown(
    """
    Esta aplicación tiene como objetivo proporcionar una herramienta interactiva para 
    analizar y visualizar datos relacionados con lesiones autoinfligidas y muertes por suicidio. 
    
    ### ¿Qué encontrarás en esta aplicación?
    - **Visualización de datos:** Gráficos y tablas que muestran tendencias y estadísticas clave.
    - **Análisis geográfico:** Mapas interactivos para explorar datos por regiones.
    - **Reportes personalizados:** Genera reportes basados en los datos seleccionados.
    
    ### ¿Cómo empezar?
    Utiliza el menú lateral para navegar entre las diferentes secciones y explorar los datos.
    """
)

st.markdown(
    """
    <footer style="text-align: center; font-size: 16px; padding: 10px; margin-top: 50px; border-top: 1px solid #ccc;">
       <strong>Unidad de vigilancia epidemiológica de enfermedades no transmisibles, cáncer y ambiente</strong>
    </footer>
    """,
    unsafe_allow_html=True
)

