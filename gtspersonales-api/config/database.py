import mysql.connector
from mysql.connector import Error
import os

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'crudapidb')
        self.user = os.getenv('DB_USER', 'rodrigo')
        self.password = os.getenv('DB_PASSWORD', 'R0dr1nt3l')
        self.port = os.getenv('DB_PORT', '3306')

    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            if connection.is_connected():
                print("Conexión exitosa a MySQL")
                return connection
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return None

# Singleton para la conexión
db_config = DatabaseConfig()