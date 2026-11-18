def exportacion():
    while True:
        import mysql.connector
        import pandas
        from dotenv import load_dotenv
        import os
        import sys
        import mysql.connector
        import mysql.connector.plugins.mysql_native_password
        import mysql.connector.locales.eng
        import cryptography
        import certifi
        import win32security

        if getattr(sys, "frozen", False):
            ruta_base = sys._MEIPASS
        else:
            ruta_base = os.path.dirname(os.path.abspath(__file__))

        # Carga las variables del .env
        load_dotenv(r"C:\Users\Usuario\OneDrive\Documentos\.Codigos\.env")

        # CONECCION MySQL.
        connection = {
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASSWORD'),
            'host': os.environ.get('DB_HOST'),
            'database': os.environ.get('DB_NAME2'),
            'port': 3306}

        # CREAMOS UNA FUNCION NORMALIZADORA OPTIMA PARA ESTE CASO ESPECIFICO 
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


        # MENU DE DOS OPCIONES.
        seleccion = input(' MENU:\n 1: Listado-Verser\n 2: Listado-Super Optica\n')

        # SE COMIENZA EL PROCESO PARA LA LISTA DE VERSER.
        if seleccion.strip() == '1':
            # TOMA LOS DATOS DEL .EXE
            data_frame = pandas.read_excel('Lista_Verser.xlsx', sheet_name=1)
            # SE DEFINEN LAS LISTAS A EXPORTAR.
            numeros_de_ordenes = data_frame['#Orden']
            clientes = data_frame['Cliente']
            emails = data_frame['CORREO']
            #CORRECCION DE FECHAS CON PANDAS.
            fechas = pandas.to_datetime(data_frame['Fecha'], dayfirst=True).dt.date.tolist()
            print('LOS DATOS DEL DOCUMENTO SE HAN LEIDO CORRECTAMENTE')

            # INICIAMOS CONECCION CON LA BASE DE DATOS.
            with mysql.connector.connect(**connection) as conn:
                cur = conn.cursor()

                # EJECUTAR DEF NORMALIZADOR.
                ids_clientes = normalizadora(clientes, 'cliente')
                ids_emails = normalizadora(emails, 'email')
                print('DATOS NORMALIZADOS')

                datos = []
                # VERIFICAMOS SI EL NUMERO DE ORDEN FUE GUARDADO PREVIAMENTE O SI AUN TIENE LUGAR.
                for numero_de_orden, fecha, id_cliente, id_email in zip(numeros_de_ordenes, fechas, ids_clientes, ids_emails):
                    cur.execute('SELECT 1 FROM verser WHERE numero_de_orden=%s', (numero_de_orden,))
                    orden = cur.fetchone()
                    if orden:
                        print('ESTE NUMERO DE ORDEN YA EXISTE EN LA BASE DE DATOS: ', numero_de_orden)
                    else:
                        print('ORDEN APROVADA: ', numero_de_orden)
                        # CREAMOS UNA TUPLA DE LISTAS.
                        datos.append((numero_de_orden, fecha, id_cliente, id_email))

                # SE INGRESAN LA LISTAS COMPLETAS CON .EXECUTEMANY
                cur.executemany('''INSERT IGNORE INTO verser(numero_de_orden, fecha, id_cliente, id_email) VALUES (%s, %s, %s, %s)''', datos)

                conn.commit()
                print('PROCESO TERMINADO CON VERSER.')
                break


        # SE COMIENZA EL PROCESO PARA LA LISTA DE SUPER OPTICA.
        elif seleccion.strip() == '2':
            # TOMA LOS DATOS DEL .EXE
            data_frame = pandas.read_excel('Lista_Super_Optica.xlsx', dtype={'Documento': str, 'celular': str}).fillna('')
            # SE COMIENZA CON EL PROCESO DE UNIR LOS NOMBRES DE LOS CLIENTES
            nombres = data_frame['Nombre1']
            segundos_nombres = data_frame['Nombre2']
            apellidos = data_frame['Apellido1']
            segundos_apellidos = data_frame['Apellido2']
            
            nombres_completos = list()
            for nombre, segundo_nombre, apellido, segundo_apellido in zip(nombres, segundos_nombres, apellidos, segundos_apellidos):
                fragmentos = [str(nombre).strip(), str(segundo_nombre).strip(), str(apellido).strip(), str(segundo_apellido).strip()] # LOS FRAGMENTO COMPONEN UNA LISTA

                fragmentos_unidos = list()
                for fragmento in fragmentos:
                    if fragmento:
                        fragmentos_unidos.append(fragmento.strip())
                nombre_completo = ' '.join(fragmentos_unidos)

                nombres_completos.append(nombre_completo.upper())
            print('AJUSTE DE NOMBRE TERMINADO')

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

            # INICIAMOS CONECCION CON LA BASE DE DATOS.
            with mysql.connector.connect(**connection) as conn:
                cur = conn.cursor()

                # EJECUTAR DEF NORMALIZADOR.
                ids_clientes = normalizadora(clientes, 'cliente')
                ids_tipo_de_documentos = normalizadora(tipo_de_documentos, 'tipo_de_documento')
                ids_documentos = normalizadora(documentos, 'documento')
                ids_celulares = normalizadora(celulares, 'celular')
                ids_emails = normalizadora(emails, 'email')
                ids_direcciones = normalizadora(direcciones, 'direccion')
                print('Datos normalizados')

                datos = []
                for numero_de_orden, fecha, id_cliente, id_tipo_de_document, id_documento, id_celular, id_email, id_direccion in zip(numeros_de_ordenes, fechas, ids_clientes, ids_tipo_de_documentos, ids_documentos, ids_celulares, ids_emails, ids_direcciones):
                    cur.execute('SELECT 1 FROM super_optica WHERE numero_de_orden=%s', (numero_de_orden,))
                    orden = cur.fetchone()
                    if orden:
                        print('ESTE NUMERO DE ORDEN YA EXISTE EN LA BASE DE DATOS: ', numero_de_orden)
                    else:
                        print('ORDEN APROVADA: ', numero_de_orden)
                        # CREAMOS UNA TUPLA DE LISTAS, CON LOS DDATOS APROVADOS.
                        datos.append((numero_de_orden, fecha, id_cliente, id_tipo_de_document, id_documento, id_celular, id_email, id_direccion))

                # SE INGRESAN LA LISTAS COMPLETAS CON .EXECUTEMANY
                cur.executemany('''INSERT IGNORE INTO super_optica(numero_de_orden, fecha, id_cliente, id_tipo_de_documento, id_documento, 
                                id_celular, id_email, id_direccion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                                datos)
                
                conn.commit()
                print('PROCESO TERMINADO CON VERSER.')
                break

        # REGRESO AL MENU EN CASO DE NO SEGUIR LA LOGICA DEL MENU.
        else:
            print('>:C')
            input('PRESS ENTER')
            continue



# EJEECUCION DEL DEF DEL CODIGO.
exportacion()