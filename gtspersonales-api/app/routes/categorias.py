from models.database import get_db_connection
import pymysql

class Categoria:
    @staticmethod
    def obtener_todas():
        """
        Obtener todas las categorías
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error al obtener categorías: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_por_id(categoria_id):
        """
        Obtener categoría por ID
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, descripcion FROM categorias WHERE id = %s",
                    (categoria_id,)
                )
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error al obtener categoría: {e}")
            return None
        finally:
            if conn:
                conn.close()