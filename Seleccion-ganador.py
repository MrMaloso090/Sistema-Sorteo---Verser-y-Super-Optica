def seleccion_de_ganador(tabla, semanal_o_mensual, columna):
    import requests
    from bs4 import BeautifulSoup
    import mysql.connector
    from dotenv import load_dotenv
    import os
    from datetime import date, timedelta

    # SE TOMAN LOS DATOS DEL .ENV
    load_dotenv()
    conection = {
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME2'),
        'port': 3306}

    # SE HACE UN SCRAPING WEB EN LA PAGINA DE RESULTADOS DE LA LOTERIA DE MEDELLIN, EN BUSCA DEL NUMERO GANADOR.
    url = "https://loteriademedellin.com.co/resultados/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    contenedor_numero_ganador = soup.find("div", class_="elementor-lottery-jackpot-information")

    datos_en_texto = contenedor_numero_ganador.get_text(", ", strip=True)

    lista_de_datos = datos_en_texto.split(', ')

    # FECHA DEL SORTEO Y NUMERO GANADOR !!
    fecha_sorteo = lista_de_datos[2].strip()
    numero_ganador = lista_de_datos[4].strip()

    # TRADUCE LA HORA A COMO LA NECESITA MYSQL.
    meses = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12}

    dia, mes, anio = fecha_sorteo.split('/')
    fecha_sorteo = date(int(anio), meses[mes], int(dia))

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

    # SE BUSCA UN PARTISIPANTE GANADOR A PARTIR DE SUS LISTAS DE NUMEROS.
    with mysql.connector.connect(**conection) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT numero_de_orden, {columna} FROM {tabla} WHERE fecha >= %s AND fecha <= %s', (fecha_inicial, fecha_final))
        respuesta = cur.fetchall()
        print('Respuesta a la consulta MySQL terminada')

        ganador_encontrado = False
        for orden, codigos in respuesta:
            lista_codigos = codigos.split(',')
            for codigo in lista_codigos:
                if str(codigo).strip() == str(numero_ganador).strip():
                    print(f'Ganador: {orden}\nNumero Ganado: {codigo}\nFecha: {fecha_sorteo}')
                    orden_ganadora =  orden
                    codigo_ganador = codigo
                    ganador_encontrado = True
                    break
                else:
                    continue
            if ganador_encontrado:
                break

        # LOS DATOS DEL GANADOR SON GUARDADOS EN SU RESPECTIVA TABLA.
        if semanal_o_mensual == 'semanal':
            tabla_ganador = 'ganador_semanal_super_optica'
        if semanal_o_mensual == 'mensual':
            tabla_ganador = 'ganador_mensual_super_optica'

        cur.execute(f'SELECT * FROM {tabla} WHERE numero_de_orden = %s', (orden_ganadora,))
        datos_ganador = cur.fetchone()
        print(datos_ganador)
        
        cur.execute(f'''INSERT INTO {tabla_ganador}(numero_de_orden, fecha_de_el_sorteo, numero_ganador, id_cliente, id_tipo_de_documento, id_documento, id_celular, id_email, id_direccion, fecha_compra) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                    (orden_ganadora, fecha_sorteo, codigo_ganador, datos_ganador[2], datos_ganador[3], datos_ganador[4], datos_ganador[5], datos_ganador[6], datos_ganador[7], datos_ganador[1]))
        conn.commit()
        print('Finalizado')




# SE EJECUTA LA DEFINICION Y SE USA UN TRY EXCEPT CON ESTEROIDES.
import traceback
try:
    seleccion_de_ganador('super_optica', 'semanal', 'codigos_semanales')
except Exception as e:
    print(e)
    traceback.print_exc()