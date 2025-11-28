#!/bin/bash

# Este script se ejecuta en la fase de 'Run' de Render (no en el Build),
# garantizando que las variables de entorno de Render están disponibles.

echo "--- Paso 1/2: Ejecutando db_init.py para crear/verificar tablas ---"

# Ejecutar el script de inicialización de la BD. 
# El comando 'set -e' asegura que el script se detenga si 'db_init.py' falla.
set -e
python db_init.py

echo "--- Paso 2/2: Iniciando servidor Uvicorn ---"
# Iniciar el servidor Uvicorn con el puerto 10000 que está expuesto en el Dockerfile.
uvicorn main:app --host 0.0.0.0 --port 10000