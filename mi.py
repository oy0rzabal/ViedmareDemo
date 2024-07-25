
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
departamentos = pd.read_csv('CatEmpleados.csv')

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
            empresas_df = pd.read_csv(empresas_file_path)
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
    # Mostrar el contenido del dashboard
    st.subheader("Welcome to the dashboard!")
    user_data = st.session_state['user_data']
    
    st.write(f"Username: {user_data['Usuario']}")
    st.write(f"Company Name: {user_data['NombreEmpresa']}")
    
    # Botón de salida
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['user_data'] = None
        st.success("You have been logged out.")

    # Aquí puedes continuar con el resto de tu código para mostrar el contenido
    # Contenido del dashboard
    st.subheader("📈 Business Analytics Dashboard")
    selected = option_menu(
        menu_title=None,
        options=["Home"],
        icons=["house"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

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
    query_CAtEmpleado="""
            select * from CatEmpleados;
            """
    horaa = execute_query(query_CAtEmpleado)


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
    #BitAsistencia
    query_asistencia="""
    select * from vBitAsistencias;
    """
    bit_asistencia = execute_query(query_asistencia)

    #Seleccion de Filtro--------
    datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
    # Filtrar df_bit_asistencia según los datos finales seleccionados
    empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()
    bit_asistencia = bit_asistencia[bit_asistencia['IdDepartamento'].isin(empleados_ids)]

    #FiltrodeFechas
    bit_asistencia['Fecha'] = pd.to_datetime(bit_asistencia['Fecha'], format='%d/%m/%Y')
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



    query_CAtEmpleado="""
    select * from CatEmpleados;
    """
    hora2 = execute_query(query_CAtEmpleado)

    # Función para gráficos de pie y barras
    def gra1():
        # Crea tres columnas
        div1,div2 = st.columns(2)
        # Gráfico circular en la primera columna
        with div1:
            query_asistencia="""
            select * from vBitAsistencias;
            """
            df_bit_asistencia1 = execute_query(query_asistencia)

            datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
            # Filtrar df_bit_asistencia según los datos finales seleccionados
            empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()
            df_bit_asistencia1 = df_bit_asistencia1[df_bit_asistencia1['IdDepartamento'].isin(empleados_ids)]

            # Sincronizamos las fechas:
            df_bit_asistencia1['Fecha'] = pd.to_datetime(df_bit_asistencia1['Fecha'], format='%d/%m/%Y')
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
                title='Tipo de ',
                labels={'Cantidad': 'Número de Consultas', 'Tipo': 'Cantidad'}
            )

        

            fig.update_layout(
                title_font_size=24,
                legend_title='Consultas',
                legend_font_size=14,
                width=400,  # Ajustar el ancho de la gráfica
                height=600  # Ajustar el alto de la gráfica
            )

            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig)
    #-------------------------------------------------------------------------------------------------------       
        # Gráfico de barras simple Incidencias por Mes
        with div2:
            # CIncidencias
            query_BitIncidencias="""
                    select * from vBitIncidencias;
                    """
            df_bitinicidencias1 = execute_query(query_BitIncidencias)


            # Sincronizamos las fechas:
            df_bitinicidencias1['FechaAlta'] = pd.to_datetime(df_bitinicidencias1['FechaAlta'], format='%d/%m/%Y')
            df_bitinicidencias1 = df_bitinicidencias1[
                (df_bitinicidencias1['FechaAlta'] >= date1) & (df_bitinicidencias1['FechaAlta'] <= date2)
            ]

            #-------------------------------------------------------------------------------------------------
            datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
            # Filtrar df_bit_asistencia según los datos finales seleccionados
            empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()

            # Filtrar por IdDepartamento
            df_bitinicidencias1 = df_bitinicidencias1[
                df_bitinicidencias1['IdEmpleado'].isin(empleados_ids)
            ].copy()

            # Agrupar por mes y nombre, y contar las ocurrencias
            df_bitinicidencias1['Mes'] = df_bitinicidencias1['FechaAlta'].dt.strftime('%B')
            data_incidentes = df_bitinicidencias1.groupby(['Mes', 'Nombre']).size().reset_index(name='Count')
            st.write(data_incidentes)


            # Crear un gráfico de barras con Plotly
            fig1 = px.bar(data_incidentes, x='Nombre', y='Count', title=f'Incidentes en {date1}')
            fig1.update_layout(width=500, height=500)  # Ajustar tamaño de la gráfica
            st.plotly_chart(fig1)

            
    # Empleados: Alta y Dado de baja((Terminado))
    # Eventos: Registro, Incidencias((Terminado)), Jornadas, Horarios
    # Reportes:
    # Llamar a la función barchart con la variable CatEmpleados

    # #------------------------------------------------------------------------- = Primera Tira de Graficas
    #Segunda tira
    #CAtEmpleado


    #bar chart--------------------------Arreglar
    def gra2():
        d1,d2 = st.columns(2)
        with d1:
            query_CAtEmpleado="""
            select * from CatEmpleados;
            """
            Emle1 = execute_query(query_CAtEmpleado)

            #Obtenemos los Filtros:
            datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
            # Filtrar df_bit_asistencia según los datos finales seleccionados
            empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()
            Emle1 = Emle1[Emle1['IdDepartamento'].isin(empleados_ids)]

            Emle1=Emle1[['IdDepartamento','IdStatus','Sexo','IdEmpresa']]

                    # Convertir valores True/False a 1/0 en IdStatus
            Emle1['IdStatus'] = Emle1['IdStatus'].replace({True: 1, False: 0})

            # Filtrar el DataFrame según las condiciones especificadas
            filtro1 = (Emle1['IdEmpresa'] == 7.0) & (Emle1['IdStatus'] == 1) & (Emle1['Sexo'] == 1)
            filtro2 = (Emle1['IdEmpresa'] == 7.0) & (Emle1['IdStatus'] == 1) & (Emle1['Sexo'] == 2)
            CatEmpleado_filtrado = Emle1[filtro1]
            CatEmpleado_filtrado1 = Emle1[filtro2]

            # Contar el número de filas que cumplen con las condiciones
            h = CatEmpleado_filtrado.shape[0]
            m = CatEmpleado_filtrado1.shape[0]

            data_consultas = {
                'Tipo': ['Hombres', 'Mujeres'],
                'Cantidad': [h, m]
            }
            df_consultas = pd.DataFrame(data_consultas)

            # Crear un gráfico circular con los datos
            fig = px.pie(
                df_consultas,
                names='Tipo',
                values='Cantidad',
                title='Numero de Personal',
                labels={'Cantidad': 'Número de Consultas', 'Tipo': 'Tipo de Consulta'},
                color_discrete_map={'Hombres': 'blue', 'Mujeres': 'pink'}  # Colores personalizados
            )

            fig.update_layout(
                title_font_size=24,
                legend_title='Tipo de Sexo',
                legend_font_size=14,
                width=400,  # Ajustar el ancho de la gráfica
                height=600  # Ajustar el alto de la gráfica
            )
            st.plotly_chart(fig)

        with d2: #Continuar Editando
            #CAtEmpleado
            query_asistencia_total = """
            select BA.Fecha, BA.Entrada, BA.Salida, CE.Clave, CE.Nombre, CE.ApP 
            from BitAsistencias AS BA 
            left join CatEmpleados AS CE ON BA.IdEmpleado = CE.IdEmpleado 
            where BA.IdEmpresa = 7 and BA.Fecha between convert(date, '27/05/2024', 103) and convert(date, '03/06/2024', 103)
            select * from vBitAsistencias where IdEmpresa = 7 and Fecha between convert(date, '27/05/2024', 103) and convert(date, '03/06/2024', 103)"""
            a_total=execute_query(query_asistencia_total)

            
    #Grafico 3----------------------------------------------------------------


    def gra3():
        gr1, gr2 = st.columns(2)
        with gr1:
            query_CAtEmpleado = """
            select * from CatEmpleados;
            """
            CtEmpleadod = execute_query(query_CAtEmpleado)

            datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
            empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()
            CtEmpleadod = CtEmpleadod[CtEmpleadod['IdDepartamento'].isin(empleados_ids)]

            # Filtrar por rango de fechas
            CtEmpleadod = CtEmpleadod[(CtEmpleadod['FechaAlta'] >= date1) & (CtEmpleadod['FechaAlta'] <= date2)]

            CtEmpleadod['FechaAlta'] = pd.to_datetime(CtEmpleadod['FechaAlta']).dt.date

                    # Crear una nueva columna 'Mes' con el mes y año de 'FechaAlta'
            CtEmpleadod['Mes'] = pd.to_datetime(CtEmpleadod['FechaAlta']).dt.to_period('M')

                    # Reemplazar True/False con 'Alta'/'Baja'
            CtEmpleadod['IdStatus'] = CtEmpleadod['IdStatus'].replace({True: 'Alta', False: 'Baja'})
                    
                    # Contar las altas y bajas por mes
            status_counts = CtEmpleadod.groupby(['Mes', 'IdStatus']).size().reset_index(name='Count')
                    
                    # Pivotar el DataFrame para que cada tipo de status (Alta/Baja) tenga su propia columna
            status_counts_pivot = status_counts.pivot(index='Mes', columns='IdStatus', values='Count').fillna(0).reset_index()

            st.write(status_counts_pivot)

        with gr2:
            query_CAtEmpleado = """
            select * from CatEmpleados;
            """

            # Suponiendo que ya has ejecutado la consulta y tienes el DataFrame CAEmpleado
            CAEmpleado = execute_query(query_CAtEmpleado)

            datos_filtrados_dep = df_merged[df_merged['Nombre_dep'] == dep]
            empleados_ids = datos_filtrados_dep['IdDepartamento'].unique()

            CAEmpleado = CAEmpleado[CAEmpleado['IdDepartamento'].isin(empleados_ids)].copy()

            # Aplicar las condiciones de filtrado de Personal Activado
            activado = CAEmpleado[(CAEmpleado['IdEmpresa'] == 7) & (CAEmpleado['IdStatus'] == 1)]
            count_activado = activado['IdStatus'].count()

            # Aplicar las condiciones de filtrado de Personal Desactivado
            desactivado = CAEmpleado[(CAEmpleado['IdEmpresa'] == 7) & (CAEmpleado['IdStatus'] == 0)]
            count_desactivado = desactivado['IdStatus'].count()

            st.title('Gráfico de Personal')

            # Crear la gráfica de barras con Plotly
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=['Activado', 'Desactivado'],
                y=[count_activado, count_desactivado],
                marker_color=['green', 'red']  # Colores verde y rojo
            ))

            fig.update_layout(
                yaxis_title='Cantidad',
                title_font_size=15,
                width=500,  # Ajustar el ancho de la gráfica (puedes cambiar este valor según tus necesidades)
                height=500  # Ajustar el alto de la gráfica (puedes cambiar este valor según tus necesidades)
            )

            # Mostrar la gráfica en Streamlit
            st.plotly_chart(fig)


    #-----------------------------------------------------------------------------------------------------------------------------------------#



    def gra4():
        gra1, gra2=st.columns(2)
        with gra1:
            query_CAtEmpleado="""
            select * from vBitEventos where IdEmpresa = 7 and Fecha between convert(date, '01/01/2024', 103) and convert(date, '03/06/2024', 103)

            """
                    # Suponiendo que ya has ejecutado la consulta y tienes el DataFrame CAEmpleado
            eventos = execute_query(query_CAtEmpleado)
            eventos_filtro = eventos[eventos['IdEmpleado'].isin(empleados_ids)]
            st.write("Evnto Total:", eventos_filtro)

        with gra2:


            # Contar los eventos por tipo de registro
            huella = eventos[eventos['IdTipoRegistro'] == 2].shape[0]
            lista = eventos[eventos['IdTipoRegistro'] == 1].shape[0]
            app = eventos[eventos['IdTipoRegistro'] == 3].shape[0]
            web = eventos[eventos['IdTipoRegistro'] == 4].shape[0]
            

            # Crear un DataFrame con los resultados
            data = {
                'TipoRegistro': ['Huella', 'Lista/Manual', 'App', 'Web'],
                'Total': [huella, lista, app, web]
            }
            df = pd.DataFrame(data)

            # Crear un gráfico de barras con Plotly Express
            fig = px.bar(df, x='TipoRegistro', y='Total', title='Total de Eventos por Tipo de Registro')

            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)


    # #------------------------------------------------------------------------------Incidencias Numero

    # #Incidencias por Mes
    #Retorno de las Funciones de los Graficos:
    if selected=="Home":
        gra1()
        gra2()
        gra3()
        gra4()

                #Graficas:
            #     Incidecias por Mes . barras verticales #Echa
            # Eventos - Barras Horizontal #Falta
            # Reportes por Mes- graficas de Lineas
            # Proporcion de Consultas por Tipo - Barra Circulas #Echa
            # Altas y Bjas por Mes - Barras


#---------------------------------------------------------------------------------------------·#
#Salida del Inicio de Sesion:

