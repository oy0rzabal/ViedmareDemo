import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd

import pyodbc

# # Configuración de la conexión
# server = '52.170.32.60'
# database = 'VIEDMARE_DB_QA'
# username = 'su'
# password = 'Oyorzabal0514'
# driver = '{ODBC Driver 18 for SQL Server}'  # Asegúrate de que el nombre del controlador sea correcto

# # Crear la cadena de conexión con TrustServerCertificate=yes
# connection_string = (
#     f'DRIVER={driver};'
#     f'SERVER={server};'
#     f'PORT=1433;'
#     f'DATABASE={database};'
#     f'UID={username};'
#     f'PWD={password};'
#     f'TrustServerCertificate=yes;'
# )

# # Conectar a la base de datos
# try:
#     with pyodbc.connect(connection_string) as conn:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT * FROM sys.databases")
#             row = cursor.fetchone()
#             while row:
#                 print(str(row[0]) + " " + str(row[1]))
#                 row = cursor.fetchone()
# except pyodbc.Error as e:
#     print(f"Error en la conexión: {e}")


import pandas as pd
from sqlalchemy import create_engine

# Configuración de la conexión
server = '52.177.20.85'
database = 'VIEDMARE_CLOCK_QA'
username = 'su'
password = 'Oyorzabal1906'
driver = 'ODBC Driver 18 for SQL Server'

# Crear la cadena de conexión usando SQLAlchemy
connection_string = (
    f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"
)

# Crear el motor de SQLAlchemy
engine = create_engine(connection_string)

# Función para ejecutar una consulta y devolver un DataFrame
def execute_query(query):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            return df
    except Exception as e:
        print(f"Error en la conexión: {e}")
        return None

# Consulta SQL
query_empleados = """
select * from BitAsistencias;"""
# query_empleados="""
# # select BA.Fecha, BA.Entrada, BA.Salida, CE.Clave, CE.Nombre, CE.ApP from BitAsistencias AS BA 
# # left join CatEmpleados AS CE ON BA.IdEmpleado = CE.IdEmpleado where BA.IdEmpresa = 7 and BA.Fecha between conve3rt(date, '27/05/2024', 103) and convert(date, '03/06/2024', 103)

# # """


# # # # Ejecutar la consulta y obtener los resultados
df_empleados = execute_query(query_empleados)

# # #Imprimir los resultados
if df_empleados is not None:
    print(df_empleados)
else:
    print("No se pudieron obtener los datos.")



#SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS

# # #   # Ejecutar las consultas
# tables_df = execute_query(query_empleados)
# csv_file = 'BitAsistencias.csv'
# print("Tablas en la base de datos 'VIEDMARE_DB_QA':")
# print(tables_df.to_csv(csv_file, index=False))
