from mysql.connector import Error
from config.database import db_config
from models.categoria import Categoria, CategoriaCreate, CategoriaUpdate
from typing import List, Optional, Tuple, Any, cast
import bcrypt
from datetime import datetime, date

class CategoriaService:
    def __init__(self):
        self.db_config = db_config

    async def get_all_categorias_async(self) -> List[Categoria]:
        """Obtiene todos los usuarios"""
        connection = self.db_config.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, nombre, descripcion, fecha_creacion, fecha_actualizacion
                FROM categorias
            """
            cursor.execute(query)
            # Guardar resultados en variable local
            categorias = cursor.fetchall()

            print(f"DEBUG - Total registros: {len(categorias)}")
            # Use pydantic's model_validate to construct models from DB dicts
            return [Categoria.model_validate(categoria) for categoria in categorias]
                
        except Error as e:
            print(f"Error al obtener categorias: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def get_categoria_by_id_async(self, categoria_id: int) -> Optional[Categoria]:
        """Obtiene un usuario por ID"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, nombre, descripcion, fecha_creacion, fecha_actualizacion
                FROM categorias 
                WHERE id = %s
            """
            cursor.execute(query, (categoria_id,))
            categoria = cursor.fetchone()

            return Categoria.model_validate(categoria) if categoria else None
            
        except Error as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            try:
                if connection and connection.is_connected():
                    # cursor may already be closed; guard defensively
                    try:
                        cursor.close()
                    except Exception:
                        pass
                    connection.close()
            except Exception:
                pass

    async def get_categoria_by_nombre_async(self, categoria_nombre: str) -> Optional[Categoria]:
        """Obtiene un Categoria por nombre"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, nombre, descripcion, fecha_creacion, fecha_actualizacion
                FROM categorias 
                WHERE nombre = %s
            """
            cursor.execute(query, (categoria_nombre,))
            categoria = cursor.fetchone()

            return Categoria.model_validate(categoria) if categoria else None
            
        except Error as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            try:
                if connection and connection.is_connected():
                    # cursor may already be closed; guard defensively
                    try:
                        cursor.close()
                    except Exception:
                        pass
                    connection.close()
            except Exception:
                pass

    async def create_categoria_async(self, categoria_data: CategoriaCreate) -> Optional[Categoria]:
        """Crea una nueva categoría"""
        connection = self.db_config.get_connection()
        if not connection:
            raise Exception("No se pudo conectar a la base de datos")
        
        try:
            cursor = connection.cursor(dictionary=True)
            now = datetime.now()
            
            query = """
                INSERT INTO categorias (nombre, descripcion, fecha_creacion)
                VALUES (%s, %s, %s)
            """
            values = (
                categoria_data.nombre,
                categoria_data.descripcion,
                now #,
                #now
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            # Obtener la categoría recién creada
            categoria_id = cursor.lastrowid or -1
            return await self.get_categoria_by_id_async(categoria_id)
            
        except Error as e:
            connection.rollback()
            raise Exception(f"Error al crear categoría: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def update_categoria_async(self, categoria_id: int, categoria_data: CategoriaUpdate) -> Optional[Categoria]:
        """Actualiza una categoría existente"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            now = datetime.now()
            
            query = """
                UPDATE categorias 
                SET nombre = %s, descripcion = %s, fecha_actualizacion = %s
                WHERE id = %s
            """
            values = (
                categoria_data.nombre,
                categoria_data.descripcion,
                now,
                categoria_id
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            if cursor.rowcount > 0:
                return await self.get_categoria_by_id_async(categoria_id)
            return None
            
        except Error as e:
            connection.rollback()
            print(f"Error al actualizar categoría: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def delete_categoria_async(self, categoria_id: int) -> bool:
        """Elimina una categoría"""
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # Verificar si hay gastos asociados a esta categoría
            check_query = "SELECT COUNT(*) as count FROM gastos WHERE categoria_id = %s"
            cursor.execute(check_query, (categoria_id,))
            row = cast(Tuple[Any, ...], cursor.fetchone())
            result = row[0]
            
            if result > 0:
                raise Exception("No se puede eliminar la categoría porque tiene gastos asociados")
            
            # Eliminar la categoría
            delete_query = "DELETE FROM categorias WHERE id = %s"
            cursor.execute(delete_query, (categoria_id,))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()