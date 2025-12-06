from typing import Any
from config.database import db_config

def get_connection() -> Any:
    """
    Obtener conexión a la base de datos
    """
    try:
        connection = db_config.get_connection()
        if connection and connection.open:
            return connection
        else:
            raise Exception("No se pudo establecer conexión con la base de datos")
    except Exception as e:
        print(f"Error en get_db_connection: {e}")
        raise e