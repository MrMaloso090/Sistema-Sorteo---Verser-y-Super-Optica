import mysql.connector
import pandas
from dotenv import load_dotenv
import os

# Carga las variables del .env
load_dotenv()

# CONECCION MySQL.
connection = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME2'),
    'port': 3306}

# TOMA LOS DATOS DEL .EXE
data_frame = pandas.read_excel('Listado.xlsx', dtype={'Documento': str, 'celular': str}).fillna('')

# UNIR NOMBRES Y APELLIDOS
nombres = data_frame['Nombre1']
segundos_nombres = data_frame['Nombre2']
apellidos = data_frame['Apellido1']
segundos_apellidos = data_frame['Apellido2']
print('Tados tomados')

nombres_completos = list()
for nombre, segundo_nombre, apellido, segundo_apellido in zip(nombres, segundos_nombres, apellidos, segundos_apellidos):
    fragmentos = [str(nombre).strip(), str(segundo_nombre).strip(), str(apellido).strip(), str(segundo_apellido).strip()] # LOS FRAGMENTO COMPONEN UNA LISTA

    fragmentos_unidos = list()
    for fragmento in fragmentos:
        if fragmento:
            fragmentos_unidos.append(fragmento.strip())
    nombre_completo = ' '.join(fragmentos_unidos)

    nombres_completos.append(nombre_completo.upper())
print('Ajuste de nombres terminado')

# SE DEFINEN LAS LISTAS A EXPORTAR.
numeros_de_ordenes = data_frame['NOrdenPedido']
clientes = nombres_completos
tipo_de_documentos = data_frame['tipodocumento']
documentos = data_frame['Documento']
celulares = data_frame['celular']
emails = data_frame['correo']
direcciones = data_frame['Direccion']
#CORRECCION DE FECHAS CON PANDAS.
fechas = pandas.to_datetime(data_frame['FechaVenta'], dayfirst=True).dt.date.tolist()
print('fechas correjidas')

# SE GUARDAN LOS DATOS DENTRO DE LA VASE.
with mysql.connector.connect(**connection) as conn:
    cur = conn.cursor()

    # LLEGO LA HORA DE NORMALIZAR.
    def normalizadora(datos, nombre):
        lista_de_ids = list()
        for dato in datos:
            if dato:
                cur.execute(f'INSERT IGNORE INTO {nombre}({nombre}) VALUES (%s)', (dato, ))
                cur.execute(f'SELECT id FROM {nombre} WHERE {nombre} = %s', (dato, ))
                id_ = cur.fetchone()
                lista_de_ids.append(id_[0] if id_ else None)
            else:
                lista_de_ids.append(None)

        return lista_de_ids

    # EJECUTAR DEF NORMALIZADOR.
    ids_clientes = normalizadora(clientes, 'cliente')
    ids_tipo_de_documentos = normalizadora(tipo_de_documentos, 'tipo_de_documento')
    ids_documentos = normalizadora(documentos, 'documento')
    ids_celulares = normalizadora(celulares, 'celular')
    ids_emails = normalizadora(emails, 'email')
    ids_direcciones = normalizadora(direcciones, 'direccion')
    print('Datos normalizados')

    for numero_de_orden in numeros_de_ordenes:
        cur.execute('SELECT 1 FROM super_optica WHERE numero_de_orden=%s', (numero_de_orden,))
        orden = cur.fetchone()
        if orden:
            print('ESTE NUMERO DE ORDEN YA EXISTE EN LA BASE DE DATOS: ', numero_de_orden)
        else:
            print('Numero autorizado: ', numero_de_orden)

    datos = list(zip(numeros_de_ordenes, fechas, ids_clientes, ids_tipo_de_documentos, ids_documentos, ids_celulares, ids_emails, ids_direcciones))
    # SE INGRESAN LA LISTAS COMPLETAS CON .EXECUTEMANY
    cur.executemany('''INSERT IGNORE INTO super_optica(numero_de_orden, fecha, id_cliente, id_tipo_de_documento, id_documento, 
                    id_celular, id_email, id_direccion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                    (datos))
    print('previo al commit')
    conn.commit()
    print('Proceso Terminado')