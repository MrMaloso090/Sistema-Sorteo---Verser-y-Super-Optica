from flask import Flask
from Distribucion_numeros import distribucion_super_optica_semanal
from Comunicacion_email import comunicacion_semanal_super_optica

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def ejecutar():

    distribucion_super_optica_semanal()

    comunicacion_semanal_super_optica()
    
    return "Distribución ejecutada correctamente", 200