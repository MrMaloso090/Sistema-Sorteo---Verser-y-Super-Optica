def distribucion_de_numero(nombre_de_la_tabla, semanal_o_mensual, columna):
    import mysql.connector
    from dotenv import load_dotenv
    import os
    import random
    from datetime import date, timedelta

    # SE TOMAN LOS DATOS DEL .ENV
    load_dotenv()
    conection = {
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME2'),
        'port': 3306}

    # LISTA CON LAS 10.000 OPCIONES DISTINTAS: (0000, 0001, 0002... 9998, 9999) #
    lista_de_codigos_a_repartir = []
    for numero in range(10000):
        codigo = str(numero).zfill(4)
        lista_de_codigos_a_repartir.append(codigo)

    # DESORDENAMOS ALEATORIAMENTE LOS 10.000 CODIGOS QUE HAY EN LA LISTA, MIENTRAS AUN SE MANTIENE COMO LISTA.
    random.shuffle(lista_de_codigos_a_repartir)

    # SE AJUSTA LA FECHA INICIAL Y LA FECHA FINAL SEGUN EL CASO. (SEMANAL O MENSUAL)
    if semanal_o_mensual == 'semanal':
        # SE ENCUENTRA EL PRIMER DIA DE LA SEMANA ACTUAL (SABADO) PARA LUEGO OPTENER LA SEMANA PASADA
        hoy = date.today()
        print('DIA ACTUAL: ', hoy)
        cantidad_de_dias_transcurridos_desde_el_sabado = (hoy.weekday() - 5) % 7 # FORMULA RE LOCA PARA ACOMODAR LOS DIAS, Y HACER QUE SABADO SEA 0 Y EL VIERNES 6.
        inicio_semana_actual_sabado = hoy - timedelta(days=cantidad_de_dias_transcurridos_desde_el_sabado)
        # PRIMER Y ULTIMO DIA DE LA SEMANA PASADA. SABADO -> VIERNES
        inicio_semana_pasada_sabado = inicio_semana_actual_sabado - timedelta(days=7)
        final_semana_pasada_viernes = inicio_semana_pasada_sabado + timedelta(days=6)
        print('FEHCAS SEMANA PASADA: ', inicio_semana_pasada_sabado, final_semana_pasada_viernes)
        # SE AJUSTA, LOS NOMBRES POR UNA OPCION GENERICA.
        fecha_inicial = inicio_semana_pasada_sabado
        fecha_final = final_semana_pasada_viernes
    if semanal_o_mensual == 'mensual':
        # SE TOMA EL EL HOY, PARA ASI BUSCAR EL PRIMER DIA DEL MES ACTUAL. PARA POSTERIORMENTE CONSEGUIR LAS FECHAS DEL MES PASADO.
        hoy = date.today()
        primer_dia_mes_actual = hoy.replace(day=1)
        # SE CONSIGUEN LAS FECHAS DEL PRIMER Y EL ULTIMO DIA DEL MES PASADO AL PRESENTE.
        ultimo_dia_mes_pasado = primer_dia_mes_actual - timedelta(days=1)
        primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
        print("FECHAS MES PASADO:", primer_dia_mes_pasado, ultimo_dia_mes_pasado)
        # SE AJUSTA, LOS NOMBRES POR UNA OPCION GENERICA.
        fecha_inicial = primer_dia_mes_pasado
        fecha_final = ultimo_dia_mes_pasado
        
    # CONECCION CON LA BASE DE DATOS.
    with mysql.connector.connect(**conection) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT numero_de_orden FROM {nombre_de_la_tabla} WHERE fecha BETWEEN %s AND %s', 
                    (fecha_inicial, fecha_final))
        jugadores = cur.fetchall()
        print('JUGADORES: ', jugadores)

    # SE RESUELVE EL MAXIMO COMUN MULTIPLO MENOR QUE 10.000, DE LA CANTIDAD DE PARTISIPANTES.
    cantidad_de_jugadores = len(jugadores)
    print('CANTIDAD DE JUGADORES: ', cantidad_de_jugadores)
    maximo_comun_multiplo = (10000 // cantidad_de_jugadores) * cantidad_de_jugadores

    # SE DIVIDE EL MAXIMO COMUN MULTIPLO ENTRE LA CANTIDAD DE PARTISIPANTES, PARA ASIGNAR LA CANTIDAD DE CODIGOS PARA CADA PARTISIPANTE.
    cantidad_de_codigos_por_jugador = (maximo_comun_multiplo // cantidad_de_jugadores)

    # AHORA SE CALCULAN LOS NUMEROS RESTANTES, PARA ALCANZAR Y REDONDEAR EL 10.000
    sobrante = 10000 - maximo_comun_multiplo

    # SE CREA UNA LISTA CON LA CANTIDAD PRECISA DE CODIGOS QUE SE LE DEBEN ASIGNAS A CADA JUGADOR.
    lista_de_grupos = [] # IMPORTANTE

    conteo_maximo_comun_multiplo = 0
    lista_codigos_sobrantes = [] # IMPORTANTE

    conteo_de_agrupaciones = 0
    agrupacion_de_codigos_por_persona = []

    for codigo in lista_de_codigos_a_repartir:
        conteo_maximo_comun_multiplo += 1
        conteo_de_agrupaciones +=1

        if conteo_maximo_comun_multiplo >= maximo_comun_multiplo:
            lista_codigos_sobrantes.append(codigo)
            continue

        agrupacion_de_codigos_por_persona.append(codigo)
        conteo_de_agrupaciones +=1

        if conteo_de_agrupaciones >= cantidad_de_codigos_por_jugador:
            grupo = ','.join(agrupacion_de_codigos_por_persona)
            lista_de_grupos.append(grupo)

            agrupacion_de_codigos_por_persona = []
            conteo_de_agrupaciones = 0

    #print('AFRUPACIONES POR PERSONA: ', lista_de_grupos)
    #print('SOBRANTES: ', lista_codigos_sobrantes)

    # SE ENTREGA UN GRUPO DE NUMEROS A CADA JUGADOR.
    with mysql.connector.connect(**conection) as conn:
        cur = conn.cursor()
        for jugador, grupo_por_persona in zip(jugadores, lista_de_grupos):
            cur.execute(f'UPDATE {nombre_de_la_tabla} SET {columna} = %s WHERE numero_de_orden = %s', (grupo_por_persona, jugador[0]))
            #print('JUGADOR Y SU GRUPO: ', jugador[0], ': ', grupo_por_persona)
        conn.commit()

    # SE ASIGNA UN JUGADOR (QUIEN SERA EL MAYOR COMPRADOR DE LA SEMANA) A QUIEN A;ADIRLE A SU GUPO DE CODIGOS LOS CODIGOS SOBRANTES.
    with mysql.connector.connect(**conection) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT id_cliente, COUNT(*) AS repeticiones FROM {nombre_de_la_tabla} WHERE fecha >= %s AND fecha <= %s GROUP BY id_cliente ORDER BY repeticiones DESC LIMIT 1", 
                    (fecha_inicial, fecha_final))
        mayor_comprador = cur.fetchone()[0]

        cur.execute(f"SELECT numero_de_orden FROM {nombre_de_la_tabla} WHERE id_cliente = %s AND fecha >= %s AND fecha <= %s ORDER BY RAND() LIMIT 1 ", 
                    (mayor_comprador, fecha_inicial, fecha_final))
        numero_de_orden_ganador = cur.fetchone()[0]
        print('NUMERO DE ORDEN GANADOR: ', numero_de_orden_ganador)

        # SE A;ADEN LOS NUMEROS SOBRANTES A EL NUMERO DE ORDEN ALEATORIO QUE LE PERTENESCA AL MAYOR COMPRADOR.
        cur.execute(f'SELECT {columna} FROM {nombre_de_la_tabla} WHERE numero_de_orden = %s', (numero_de_orden_ganador,))
        grupo_ya_asignado = cur.fetchone()[0]
        print('GRUPO PREVIO: ', grupo_ya_asignado)

        grupo_sobrante = ','.join(lista_codigos_sobrantes)
        grupo_nuevo_de_codigos = f'{grupo_ya_asignado},{grupo_sobrante}'
        print('NUEVO GRUPO: ', grupo_nuevo_de_codigos)

        cur.execute(f'UPDATE {nombre_de_la_tabla} SET {columna} = %s WHERE numero_de_orden = %s', (grupo_nuevo_de_codigos, numero_de_orden_ganador))
        conn.commit()


# SE EJECUTA LA DEFINICION Y SE USA UN TRY EXCEPT CON ESTEROIDES.
import traceback
try:
    distribucion_de_numero('super_optica', 'semanal', 'codigos_semanales')
except Exception as e:
    print(e)
    traceback.print_exc()