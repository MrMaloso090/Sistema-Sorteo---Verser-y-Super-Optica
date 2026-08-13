# Imagen ligera de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia de los archivos del proyecto
COPY . /app

# Instalacion de las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usa Flask (Cloud Run lo asignará)
ENV PORT=8080

# Comando para iniciar el servidor con gunicorn
CMD exec gunicorn --bind :$PORT main:app --workers 1 --threads 8 --timeout 0