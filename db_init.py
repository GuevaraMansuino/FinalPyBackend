import logging
import sys

# Se importan las funciones de conexión y creación de tablas
# Asumimos que config/database.py está corregido para usar DATABASE_URL
from config.database import create_tables, check_connection

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Script de inicialización de base de datos iniciado.")

# Verificar la conexión antes de intentar crear las tablas
if check_connection():
    logger.info("Conexión exitosa a la BD. Procediendo a crear tablas...")
    
    # Intentar crear las tablas
    try:
        create_tables()
        logger.info("Todas las tablas creadas exitosamente.")
        
    except Exception as e:
        logger.error(f"Error al ejecutar create_tables(): {e}")
        # Es un error de la BD, salimos con código 1 para que Render detenga el despliegue
        sys.exit(1)

else:
    # Si check_connection falla, el error es fatal
    logger.error("Error fatal: Falló la conexión inicial a la base de datos. Verifique la variable DATABASE_URL.")
    sys.exit(1)

logger.info("Script de inicialización de base de datos finalizado.")