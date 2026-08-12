def distribucion_de_numero(nombre_de_la_tabla, semanal_o_mensual, columna):
    import mysql.connector
    from dotenv import load_dotenv
    import os
    import random
    from datetime import date, timedelta
    from flask import Flask

    app = Flask(__name__)

    # SE TOMAN LOS DATOS DEL .ENV
    load_dotenv()
    conection = {
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME2'),
        'port': 3306}

    # LISTA CON LAS 10.000 OPCIONES DISTINTAS: (0000, 0001, 0002... 9998, 9999) # O SI ES SUPER OPTICA SE CREAN CODIGOS DE 3 DIGITOS (000, 001, 002...)
    if nombre_de_la_tabla == 'super_optica':
        cantidad_de_digitos = 3
        cantidad_codigos = 1000
    elif nombre_de_la_tabla == 'verser':
        cantidad_de_digitos = 4
        cantidad_codigos = 10000

    lista_de_codigos_a_repartir = []
    for numero in range(cantidad_codigos):
        codigo = str(numero).zfill(cantidad_de_digitos)
        lista_de_codigos_a_repartir.append(codigo)

    # DESORDENAMOS ALEATORIAMENTE LOS 10.000 CODIGOS QUE HAY EN LA LISTA, MIENTRAS AUN SE MANTIENE COMO LISTA.
    random.shuffle(lista_de_codigos_a_repartir)

    # ===============================================================================
    # ===============================================================================

    # SE AJUSTA LA FECHA INICIAL Y LA FECHA FINAL SEGUN EL CASO. (SEMANAL O MENSUAL)
    if semanal_o_mensual == 'semanal':
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

    if semanal_o_mensual == 'mensual':
        # SE TOMA EL EL HOY, PARA ASI BUSCAR EL PRIMER DIA DEL MES ACTUAL. PARA POSTERIORMENTE CONSEGUIR LAS FECHAS DEL MES PASADO.
        hoy = date.today()
        primer_dia_mes_actual = hoy.replace(day=1)
        # SE CONSIGUEN LAS FECHAS DEL PRIMER Y EL ULTIMO DIA DEL MES PASADO.
        ultimo_dia_mes_pasado = primer_dia_mes_actual - timedelta(days=1)
        primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
        # SE AJUSTA, LOS NOMBRES POR UNA OPCION GENERICA.
        fecha_inicial = primer_dia_mes_pasado
        fecha_final = ultimo_dia_mes_pasado
        print('MENSUAL')


    print(f'PRIMER DIA SEMANA PASADA: {fecha_inicial}')
    print(f'ULTIMO DIA SEMANA PASADA: {fecha_final}')

    # ===============================================================================
    # ===============================================================================
        
    # CONECCION CON LA BASE DE DATOS.
    with mysql.connector.connect(**conection) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT numero_de_orden FROM {nombre_de_la_tabla} WHERE fecha BETWEEN %s AND %s', 
                    (fecha_inicial, fecha_final))
        jugadores = cur.fetchall()
        if not jugadores:
            print(f'ERROR EN LA DB: NO HAY COMPRAS DE LA SEMANA PASADA')
        print('JUGADORES: ', jugadores)
        
    # SE RESUELVE EL MAXIMO COMUN MULTIPLO MENOR QUE 10.000, DE LA CANTIDAD DE PARTISIPANTES.
    cantidad_de_jugadores = len(jugadores)
    print('CANTIDAD DE JUGADORES: ', cantidad_de_jugadores)
    maximo_comun_multiplo = (cantidad_codigos // cantidad_de_jugadores) * cantidad_de_jugadores

    # SE DIVIDE EL MAXIMO COMUN MULTIPLO ENTRE LA CANTIDAD DE PARTISIPANTES, PARA ASIGNAR LA CANTIDAD DE CODIGOS PARA CADA PARTISIPANTE.
    cantidad_de_codigos_por_jugador = (maximo_comun_multiplo // cantidad_de_jugadores)

    # AHORA SE CALCULAN LOS NUMEROS RESTANTES, PARA ALCANZAR Y REDONDEAR EL 10.000
    sobrante = cantidad_codigos - maximo_comun_multiplo

    # SE CREA UNA LISTA CON LA CANTIDAD PRECISA DE CODIGOS QUE SE LE DEBEN ASIGNAS A CADA JUGADOR.
    lista_de_grupos = [] # IMPORTANTE

    conteo_maximo_comun_multiplo = 0
    lista_codigos_sobrantes = [] # IMPORTANTE

    conteo_de_agrupaciones = 0
    agrupacion_de_codigos_por_persona = []

    for codigo in lista_de_codigos_a_repartir:
        conteo_maximo_comun_multiplo += 1

        if conteo_maximo_comun_multiplo > maximo_comun_multiplo:
            lista_codigos_sobrantes.append(codigo)
            continue

        agrupacion_de_codigos_por_persona.append(codigo)
        conteo_de_agrupaciones +=1

        if conteo_de_agrupaciones >= cantidad_de_codigos_por_jugador:
            grupo = ','.join(agrupacion_de_codigos_por_persona)
            lista_de_grupos.append(grupo)

            agrupacion_de_codigos_por_persona = []
            conteo_de_agrupaciones = 0

    #print('AGRUPACIONES POR PERSONA: ', lista_de_grupos)
    #print('SOBRANTES: ', lista_codigos_sobrantes)

    # SE ENTREGA UN GRUPO DE NUMEROS A CADA JUGADOR.
    with mysql.connector.connect(**conection) as conn:
        cur = conn.cursor()
        for jugador, grupo_por_persona in zip(jugadores, lista_de_grupos):
            cur.execute(f'UPDATE {nombre_de_la_tabla} SET {columna} = %s WHERE numero_de_orden = %s', (grupo_por_persona, jugador[0]))
            print('JUGADOR Y SU GRUPO: ', jugador[0], ': ', grupo_por_persona)
        conn.commit()

    # SE REPARTEN LOS NUMEROS SOBRANTES, ASIGNANOLE UNO A DISTINTOS PARTISIPANTEZ DE FORMA AZAROSA.
        cantidad_de_numeros_sobrantes = len(lista_codigos_sobrantes)
        if cantidad_de_numeros_sobrantes != 0:
            cur.execute(f'SELECT numero_de_orden FROM {nombre_de_la_tabla} WHERE fecha >= %s AND fecha <= %s  ORDER BY RAND() LIMIT {cantidad_de_numeros_sobrantes}', (fecha_inicial, fecha_final))
            lista_de_ordenes_aleatoria = cur.fetchall()
            
            for sobrante, orden in zip(lista_codigos_sobrantes, lista_de_ordenes_aleatoria):
                cur.execute(f'SELECT {columna} FROM {nombre_de_la_tabla} WHERE numero_de_orden = %s', (orden[0],))
                grupo_asignado_previamente = cur.fetchone()[0]
                grupo_nuevo = f'{grupo_asignado_previamente},{sobrante}'
                cur.execute(f'UPDATE {nombre_de_la_tabla} SET {columna} = %s WHERE numero_de_orden = %s', (grupo_nuevo, orden[0]))
            conn.commit()




#=====================================
# SE IMPORTA UN TRY CON ESTEEROIDES.
import traceback
#=====================================

# FUNCION PARA SUPER OPTICA - *SEMANAL*
def distribucion_super_optica_semanal():
    try:
        distribucion_de_numero('super_optica', 'semanal', 'codigos_semanales')
    except Exception as e:
        print(e)
        traceback.print_exc()

# FUNCION PARA SUPER OPTICA - *MENSUAL*
def distribucion_super_optica_mensual():
    try:
        distribucion_de_numero('super_optica', 'mensual', 'codigos_mensuales')
    except Exception as e:
        print(e)
        traceback.print_exc()

# FUNCION PARA VERSER - *SEMANAL*
def distribucion_verser_semanal():
    try:
        distribucion_de_numero('verser', 'semanal', 'codigos_semanales')
    except Exception as e:
        print(e)
        traceback.print_exc()

# FUNCION PARA VERSER - *MENSUAL*
def distribucion_verser_mensual():
    try:
        distribucion_de_numero('verser', 'mensual', 'codigos_mensuales')
    except Exception as e:
        print(e)
        traceback.print_exc()

#=====================================

@app.route("/", methods=["GET", "POST"])
def ejecutar():
    distribucion_super_optica_semanal()
    return "Distribución ejecutada correctamente", 200