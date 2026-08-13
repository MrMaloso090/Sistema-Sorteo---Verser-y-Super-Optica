from flask import Flask
from Distribucion_numeros import distribucion_super_optica_semanal

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def ejecutar():
    distribucion_super_optica_semanal()
    return "Distribución ejecutada correctamente", 200