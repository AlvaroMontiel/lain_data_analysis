import streamlit as st

# Lista de usuarios autorizados
AUTHORIZED_USERS = ["admin1@example.com", "admin2@example.com"]

def check_access(user_email):
    """Verifica si el usuario tiene permisos para cargar archivos"""
    return user_email in AUTHORIZED_USERS

def login():
    """Formulario de autenticación"""
    user_email = st.text_input("Ingrese su correo")
    if st.button("Carga de Datos"):
        if check_access(user_email):
            st.success("Acceso concedido")
            return True
        else:
            st.error("Acceso denegado")
            return False
