import streamlit as st

st.set_page_config(
    page_title="Vigilancia epidemiológica de lesiones autoinfligidas y muertes por suicidio",
    page_icon="👋",
)

st.sidebar.image("assets/logo.png", width=200)

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

if __name__ == '__main__':
    import sys
    import os
    import subprocess
    from streamlit.web import cli as stcli
    from streamlit.config import set_option

    # Define port explicitly
    PORT = 8502

    # Configure Streamlit settings
    set_option('global.developmentMode', False)
    set_option('server.port', PORT)
    set_option('browser.serverPort', PORT)
    set_option('browser.serverAddress', 'localhost')
    set_option('server.address', 'localhost')

    if not hasattr(sys, 'frozen'):
        subprocess.run(["streamlit", "run", "hello.py", "--server.port", str(PORT)])
    else:
        # Get the correct path when running as frozen executable
        if getattr(sys, '_MEIPASS', None):
            # Running as PyInstaller bundle
            bundle_dir = sys._MEIPASS
            # Create necessary directories if they don't exist
            os.makedirs(os.path.join(bundle_dir, 'pages'), exist_ok=True)
            os.makedirs(os.path.join(bundle_dir, 'src'), exist_ok=True)
            
            # Set up the script path
            script_path = os.path.join(bundle_dir, 'hello.py')
            
            # Add bundle_dir to Python path so it can find the modules
            sys.path.insert(0, bundle_dir)
        else:
            script_path = __file__

        # Set up arguments for frozen mode
        sys.argv = ["streamlit", "run", script_path,
                   "--global.developmentMode", "false",
                   "--server.port", str(PORT),
                   "--server.address", "localhost",
                   "--browser.serverAddress", "localhost",
                   "--browser.serverPort", str(PORT)]
        
        try:
            # Launch the application using streamlit CLI
            sys.exit(stcli.main())
        except Exception as e:
            print(f"Error launching Streamlit: {e}")
            print(f"Script path:", script_path)
            print(f"Bundle dir:", bundle_dir if 'bundle_dir' in locals() else "Not in frozen mode")
            print(f"Try accessing the app at: http://localhost:{PORT}")
            