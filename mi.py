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
    user_data = st.session_state['user_data']
   

    # Extraer NombreEmpresa y Filtro 
    NombreEmpresa = user_data['NombreEmpresa']
    df_merged = df_merged[df_merged['Nombre_emp'] == NombreEmpresa]
    # Entrada de texto para buscar en las columnas Nombre_dep y Nombre_pues
    search_term = st.text_input('Buscar:')

    # Filtrar los datos según el término de búsqueda y el IdEmpresa del usuario autenticado
    if search_term:
        filtered_df = df_merged[
            ((df_merged['Nombre_dep'].str.contains(search_term, case=False, na=False)) |
            (df_merged['Nombre'].str.contains(search_term, case=False, na=False)) |
            (df_merged['Nombre_emp'].str.contains(search_term, case=False, na=False)))
        ]
    else:
        filtered_df = df_merged
    # Crear columnas para los selectbox
    col1, col2, col3 = st.columns(3)

    with col1:
        # Selectbox para seleccionar la empresa
        empresa = st.selectbox('Empresa:', filtered_df['Nombre_emp'].unique())
        # Filtrar los datos según la empresa seleccionada
        datos_filtrados_empresa = filtered_df[filtered_df['Nombre_emp'] == empresa]

    with col2:
        # Selectbox para seleccionar la sede
        sede = st.selectbox('Sede:', datos_filtrados_empresa['Nombre'].unique())
        # Filtrar los datos según la sede seleccionada
        datos_filtrados_sede = datos_filtrados_empresa[datos_filtrados_empresa['Nombre'] == sede]

    with col3:
        # Selectbox para seleccionar el departamento
        dep = st.selectbox('Departamento:', datos_filtrados_sede['Nombre_dep'].unique())
        # Filtrar los datos según el departamento seleccionado
        datos_filtrados_dep = datos_filtrados_sede[datos_filtrados_sede['Nombre_dep'] == dep]

    #*--------------------------------------------------------------------------------Horario
    
    horaa = pd.read_csv('CatEmpleados.csv')
    #Seleccion de Filtro--------
    datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
    # Filtrar df_bit_asistencia según los datos finales seleccionados
    empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()

    horaa = horaa[horaa['IdDepartamento'].isin(empleados_ids)]
    # #Seleccion de Fechas:
    fe1, fe2= st.columns((2))
    horaa['FechaAlta']=pd.to_datetime(horaa['FechaAlta'])
    # #DataFrame

    # #Getting the min and maz date
    startDate=pd.to_datetime(horaa['FechaAlta']).min()
    endDate=pd.to_datetime(horaa['FechaAlta']).max()

    with fe1:
        date1=pd.to_datetime(st.date_input("Inicio", startDate))
    with fe2:
        date2=pd.to_datetime(st.date_input("Fin", endDate))
    #Ponemos en orgen las Fechas:
    hora=horaa['FechaAlta'][(horaa['FechaAlta'] >= date1) & (horaa['FechaAlta']<= date2)].copy()

    #*--------------------------------------------------------------------------------Horario
    
    bit_asistencia = pd.read_csv('vBitAsistencias.csv')

    #Seleccion de Filtro--------
    datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
    # Filtrar df_bit_asistencia según los datos finales seleccionados
    empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()
    bit_asistencia = bit_asistencia[bit_asistencia['IdDepartamento'].isin(empleados_ids)]

    #FiltrodeFechas
    bit_asistencia['Fecha'] = pd.to_datetime(bit_asistencia['Fecha'], errors='coerce')
    bit_asistencia = bit_asistencia[
        (bit_asistencia['Fecha'] >= date1) & (bit_asistencia['Fecha'] <= date2)
    ]

    # Contar las incidencias
    conteos = bit_asistencia['Calificacion'].value_counts().to_dict()

    # Crear columnas para las métricas
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="Falta", value=conteos.get('Falta', 0))

    with col2:
        st.metric(label="Asistencia", value=conteos.get('Asistencia', 0))

    with col3:
        st.metric(label="Descanso", value=conteos.get('Descanso', 0))

    with col4:
        st.metric(label="Retardo", value=conteos.get('Retardo', 0))

    with col5:
        st.metric(label="Justificación", value=conteos.get('Justificacion', 0))


    # #-------------------------------------------------------------------------Numero de Empledos = Primera Tira de Graficas


    # Función para gráficos de pie y barras
    def gra1():
        # Crea tres columnas
        div1, div2 = st.columns(2)
        # Gráfico circular en la primera columna
        with div1:
            df_bit_asistencia1=pd.read_csv('vBitAsistencias.csv')

            datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
            # Filtrar df_bit_asistencia según los datos finales seleccionados
            empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()
            df_bit_asistencia1 = df_bit_asistencia1[df_bit_asistencia1['IdDepartamento'].isin(empleados_ids)]

            # Sincronizamos las fechas:
            df_bit_asistencia1['Fecha'] = df_bit_asistencia1['Fecha'] = pd.to_datetime(df_bit_asistencia1['Fecha'])
            df_bit_asistencia1 = df_bit_asistencia1[
                (df_bit_asistencia1['Fecha'] >= date1) & (df_bit_asistencia1['Fecha'] <= date2)
            ]
            

            # Contar las calificaciones
            conteos1 = df_bit_asistencia1['Calificacion'].value_counts().to_dict()

            # Asegurar que todos los tipos de calificación estén presentes en el diccionario
            conteos_completos = {'Asistencia': 0, 'Falta': 0, 'Descanso': 0}
            conteos_completos.update(conteos1)
            # Crear un DataFrame con los valores calculados
            data_consultas = {
                'Tipo': ['Asistencia', 'Faltas', 'Descansos'],
                'Cantidad': [conteos_completos['Asistencia'], conteos_completos['Falta'],conteos_completos['Descanso']]
            }

            df_consultas = pd.DataFrame(data_consultas)

            # bit_asistencia_filtrada = df_consultas[df_consultas['IdDepartamento'].isin(empleados_ids)]
            # st.write(df_consultas = pd.DataFrame(data_consultas))
            # Crear un gráfico circular con los datos
            fig = px.pie(
                df_consultas,
                names='Tipo',
                values='Cantidad',
                title='Tipo Consultas',
                labels={'Cantidad': 'Número de Consultas', 'Tipo': 'Cantidad'}
            )

        

            fig.update_layout(
                title_font_size=24,
                legend_title='Cantidad',
                legend_font_size=14,
                width=400,  # Ajustar el ancho de la gráfica
                height=600  # Ajustar el alto de la gráfica
            )

            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig)
    def gra2():
        gra2, gra3 = st.columns(2)
        # Gráfico de barras simple Incidencias por Mes
        with gra2:
            # CIncidencias
           
            incidencias = pd.read_csv('vBitIncidencias.csv')
            
            # Convertir la columna FechaAlta a datetime
            incidencias['FechaAlta'] = pd.to_datetime(incidencias['FechaAlta'])

            # Separar la fecha y la hora en columnas diferentes
            incidencias['Fecha'] = incidencias['FechaAlta'].dt.date
            incidencias['Hora'] = incidencias['FechaAlta'].dt.time
            st.write(incidencias[['Nombre', 'Observaciones', 'Fecha']])
            # Contar los tipos de datos distintos y sus frecuencias

            

        with gra3:
            value_counts = incidencias['Nombre'].value_counts().reset_index()
            value_counts.columns = ['Nombre', 'Frecuencia']

            # Graficar con plotly
            fig = px.bar(value_counts, x='Nombre', y='Frecuencia', title='Frecuencia de Tipos de Datos en la Columna Nombre')

            # Mostrar en Streamlit
            st.title('Frecuencia de Tipos de Datos')
            st.plotly_chart(fig)

#------------------------------------------------------------------------------------------------------------------------------------------------------#
    if selected=="Home":
            gra1()
            gra2()
