from flask import Flask
from Distribucion_numeros import distribucion_super_optica_semanal
from Comunicacion_email import comunicacion_semanal_super_optica
from Seleccion_ganador import ganador_super_optica_semanal

app = Flask(__name__)

# DISTRIBUYE LOS NUMEROS DE FORMA EQUITATIVA POR COMPRA. Y SE LO COMUNICA A LOS CONSUMIDORES, ENVIANDOLEES EMAILS. CADA SEMANA, PARA SUPER OPTICA.
@app.route("/distribuir_y_comunicar_los_numeros_de_el_sorteo", methods=["GET", "POST"])
def distribucion_de_numeros_y_correos():

    distribucion_super_optica_semanal()

    comunicacion_semanal_super_optica()
    
    return "Distribución ejecutada correctamente", 200

# SELECCIONA AL GANADOR Y LO GUARDA EN LA BASE DE DATOS. CADA SEMANA, PARA SUPER OPTICA.
@app.route("/selector_del_ganador_semanal_super_optica", methods=["GET", "POST"])
def selecciona_al_ganador():

    ganador_super_optica_semanal()
    
    return "Distribución ejecutada correctamente", 200