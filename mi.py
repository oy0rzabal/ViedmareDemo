import matplotlib.pyplot as plt
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import numpy as np
from numerize.numerize import numerize
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import altair as alt
#option menu
import pandas as pd
import sqlalchemy
from urllib.parse import quote_plus

import pyodbc
pd.set_option('future.no_silent_downcasting', True)

from streamlit_option_menu import option_menu
theme_plotly=None #or you can use streamlit theme
st.set_page_config(layout="wide")
#-----------------------------------------------------------------------------------------------------------#

# Ejecutar la consulta y obtener los resultados en un DataFrame
departamentos = pd.read_csv('CatDepartamentos.csv')

# Empresas:
empresas = pd.read_csv('CatEmpresas.csv')

# Sedes:
sedes = pd.read_csv('CatSedes.csv')


# Unir los DataFrames
df_merged = pd.merge(departamentos, empresas, on='IdEmpresa', suffixes=('_dep', '_emp'))
df_merged = pd.merge(df_merged, sedes, on='IdEmpresa', suffixes=('', '_sede'))

#--------------------------------------------------------------------------------------------------#
# Función de login

def login(username, password):
    # Leer el archivo CSV
    df = pd.read_csv('CatOperadores.csv')
    
    # Filtrar el DataFrame para encontrar el usuario
    user_data = df[(df['Usuario'] == username) & (df['Password'] == password)]
    
    if not user_data.empty:
        user_data = user_data.iloc[0]
        if user_data['IdStatus']:  # Asegúrate de que el estado sea True
            # Añadir la columna de NombreEmpresa desde el CSV CatEmpresas
            empresas_df = pd.read_csv('CatEmpresas.csv')
            empresa_data = empresas_df[empresas_df['IdEmpresa'] == user_data['IdEmpresa']]
            
            if not empresa_data.empty:
                user_data['NombreEmpresa'] = empresa_data.iloc[0]['Nombre']
            return user_data
        else:
            return None
    else:
        return None

# Mantener el estado de autenticación
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

# Interfaz de inicio de sesión
if not st.session_state['authenticated']:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user_data = login(username, password)
        if user_data is not None:
            st.session_state['authenticated'] = True
            st.session_state['user_data'] = user_data
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")
else:
    # Configuración inicial del título y menú
    st.subheader("📈 Business Analytics Dashboard")

    # Crear columnas para colocar los botones
    col1, col2 = st.columns([3, 1])  # Ajusta los pesos según el espacio que desees

    # Botón de inicio
    with col1:
        selected = option_menu(
            menu_title=None,
            options=["Home"],
            icons=["house"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal"
        )
    
    # Botón de logout
    with col2:
        if st.button("Logout"):
            st.session_state['authenticated'] = False
            st.session_state['user_data'] = None
            st.success("You have been logged out.")
    
    # Obtener IdEmpresa y Nombre del usuario autenticado
# Obtener los datos del usuario autenticado
    st.write( st.session_state['user_data'])
