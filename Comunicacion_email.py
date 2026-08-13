def comunicacion_con_jugadores(tabla, semanal_o_mensual, columna):
    import mysql.connector
    from dotenv import load_dotenv
    import os
    from datetime import date, timedelta
    import smtplib
    from email.mime.text import MIMEText
    import time

    # SE TOMAN LOS DATOS DEL .ENV
    load_dotenv()
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("EMAIL_PASSWORD")
    conection = {
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME2'),
        'port': 3306}

    # SE AJUSTA LA FECHA INICIAL Y LA FECHA FINAL SEGUN EL CASO. (SEMANAL O MENSUAL)
    if semanal_o_mensual == 'semanal':
        # SE ENCUENTRA EL PRIMER DIA DE LA SEMANA ACTUAL (SABADO) PARA LUEGO OPTENER LA SEMANA PASADA
        # SE TOMA COMO REFERENTE EL DIA PRESENTE.
        hoy = date.today()
        print('DIA ACTUAL: ', hoy)
        # SE ENCUENTRA EL PRIMER DIA DE LA SEMANA ACTUAL (LUNES)
        inicio_semana_actual = hoy - timedelta(days=(hoy.weekday()))
        # SE ENCUENTRA EL LUNES DE LA SEMANA PASADA.
        lunes_pasado = inicio_semana_actual - timedelta(days=7)
        # SE ENCUENTRA EL DOMINGO PASADO
        domingo_pasado = lunes_pasado + timedelta(days=6)
        # SE AJUSTA, LOS NOMBRES POR UNA OPCION GENERICA.
        fecha_inicial = lunes_pasado
        fecha_final = domingo_pasado
        print('SEMANAL')
        print("FECHAS SEMANA PASADO:", lunes_pasado, domingo_pasado)
    if semanal_o_mensual == 'mensual':
        # SE TOMA EL EL HOY, PARA ASI BUSCAR EL PRIMER DIA DEL MES ACTUAL. PARA POSTERIORMENTE CONSEGUIR LAS FECHAS DEL MES PASADO.
        hoy = date.today()
        print('DIA ACTUAL: ', hoy)
        # SE ENCUENTRA EL PRIMER DIA DEL MES ACTUAL
        primer_dia_mes_actual = hoy.replace(day=1)
        # SE CONSIGUEN LAS FECHAS DEL PRIMER Y EL ULTIMO DIA DEL MES PASADO AL PRESENTE.
        ultimo_dia_mes_pasado = primer_dia_mes_actual - timedelta(days=1)
        primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
        # SE AJUSTA, LOS NOMBRES POR UNA OPCION GENERICA.
        fecha_inicial = primer_dia_mes_pasado
        fecha_final = ultimo_dia_mes_pasado
        print('MENSUAL')
        print("FECHAS MES PASADO:", primer_dia_mes_pasado, ultimo_dia_mes_pasado)

    # RECOPILAMOS LOS JUGADORES Y SUS DATOS POR CADA COMPRA
    with mysql.connector.connect (**conection) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT id_email FROM {tabla} WHERE fecha >= %s AND fecha <= %s', (fecha_inicial, fecha_final))
        respuesta_ids_emails = cur.fetchall()

        # SE HACE UN SET QUE GUARDE CADA ID_EMAIL SOLO UNA VEZ.
        ids_email_unicos = set()
        for id_email, in respuesta_ids_emails:
            ids_email_unicos.add(id_email)

        # SE HACE UN BUCLE CON EL SET DE VALORES UNICOS, PARA OBTENER UNA LISTA DE TUPLAS UNICA CON EL EMAIL Y EL NOMBRE.
        emails_y_clientes = []
        for id_email in ids_email_unicos:
            print('ID_EMAIL: ', id_email)

            cur.execute(f' SELECT id_cliente FROM {tabla} WHERE fecha >= %s AND fecha <= %s AND id_email = %s LIMIT 1', 
                        (fecha_inicial, fecha_final, id_email))
            resultado = cur.fetchone()
            id_cliente = resultado[0] if resultado else None

            emails_y_clientes.append((id_email, id_cliente))
        

        # INGRESAMOS AL CORREO DEE VERSER Y SUPER OPTICA PARA REALIZAR LOS ENVIOS.
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(EMAIL, PASSWORD)

            # SE HACE UN BUCLE CON LA LISTA DE TUPLAS UNICAS, PARA OBTENER TODOS SUS NUMEROS DE ORDEN Y SUS NUMEROS A JUGAR Y ASI UNIR TODOS EN UN TEXTO. Y ENVIARLO POR EEMAIL.
            for id_email, id_cliente in emails_y_clientes:
                if not id_email: continue

                cada_orden_y_sus_numeros = []
                cur.execute(f' SELECT numero_de_orden, fecha, {columna} FROM {tabla} WHERE fecha >= %s AND fecha <= %s AND id_email = %s', (fecha_inicial, fecha_final, id_email))
                respuesta = cur.fetchall()
                for orden, fecha, numeros in respuesta:
                    cada_orden_y_sus_numeros.append(f'*{orden}, {fecha}*: {numeros}')

                informacion = '\n\n'.join(cada_orden_y_sus_numeros)

                ## SE OPTIENE EL EMAIL Y EL NOMBRE DEL CLIENTE.
                cur.execute('SELECT email FROM email WHERE id = %s', (id_email,))
                resultado = cur.fetchone()
                email = resultado[0] if resultado else None

                cur.execute('SELECT cliente FROM cliente WHERE id = %s', (id_cliente,))
                resultado = cur.fetchone()
                cliente = resultado[0] if resultado else None



                ## SE IMPRIMEN LOS DATOS OBTENIDOS.
                print(f'\nEMAIL: {email}\nCLIENTE: {cliente}\nINFORMACION: {informacion}\n')

                ## SE ENVIA UN CORREO POR CADA EMAIL, CLIENTE.
                mensaje = MIMEText(f'''
Hola {cliente}

Gracias por confiar en Super Óptica.

Ahora que decidiste ver el mundo de la mejor manera, queremos darte una razón más para sonreír. Desde hoy haces parte de "Consultas para decidir y ganar".

Tus números son:
{informacion}

Guárdalos muy bien. Con estos números participarás en el sorteo de esta semana, correspondiente a las compras realizadas entre el {fecha_inicial} y el {fecha_final}.

Tu compra fue registrada el:
{fecha}

El sorteo se realizará el viernes por la Lotería de Medellín. Si resultas ganador(a), te devolveremos el 100% del valor de tu compra y además recibirás $1.000.000 adicionales.

Sí, podrías estrenar tus gafas, recuperar todo lo que pagaste y recibir un millón de pesos más. Porque en Super Óptica creemos que las mejores decisiones también pueden traer grandes oportunidades.

Recuerda que cada viernes tendremos un(a) ganador(a), y el próximo podrías ser tú.

¡Mucha suerte!

Super Óptica
Para que veas el mundo de la mejor manera.
''')
                mensaje["Subject"] = f'Gracias por confiar en Super Óptica.'
                mensaje["From"] = EMAIL
                mensaje["To"] = email # email del cliente !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                try:
                        servidor.send_message(mensaje)
                except Exception as e:
                    print(f"No se pudo enviar el correo a {email}: {e}")
                    continue
                time.sleep(1)

            print("Proceso Finalizado.")



def comunicacion_semanal_super_optica():
    comunicacion_con_jugadores('super_optica', 'semanal', 'codigos_semanales')




#comunicacion_con_jugadores('super_optica', 'mensual', 'codigos_mensuales')