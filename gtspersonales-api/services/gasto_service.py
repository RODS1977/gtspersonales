from mysql.connector import Error
from config.database import db_config
from models.gasto import Gasto, GastoCreate, GastoUpdate, GastoConRelaciones
from typing import List, Optional, Tuple, Any, cast
import bcrypt
from datetime import datetime, date
from pydantic import BaseModel, EmailStr

class GastoService:
    def __init__(self):
        self.db_config = db_config

    async def get_all_gastos_async(self) -> List[GastoConRelaciones]:
        """Obtiene todos los gastos con información de relaciones"""
        connection = self.db_config.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, usuario_id, categoria_id, monto, fecha, descripcion, fecha_creacion, fecha_actualizacion
                FROM gastos
                ORDER BY fecha DESC
            """
            cursor.execute(query)
            # Guardar resultados en variable local
            gastos = cursor.fetchall()

            # Mapeo explícito para evitar problemas de tipos
            gastos = []
            for fila in gastos:
                gasto = GastoConRelaciones(
                    id=fila['id'],
                    usuario_id=fila['usuario_id'],
                    categoria_id=fila['categoria_id'],
                    monto=float(fila['monto']),
                    fecha=fila['fecha'],
                    descripcion=fila['descripcion'],
                    fecha_creacion=fila['fecha_creacion'],
                    fecha_actualizacion=fila['fecha_actualizacion'],
                    nombre_usuario=fila['nombre_usuario'],
                    nombre_categoria=fila['nombre_categoria']
                )
                gastos.append(gasto)
            
            return gastos            
                
        except Error as e:
            print(f"Error al obtener gastos: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def get_gasto_by_id_async(self, gasto_id: int) -> Optional[Gasto]:
        """Obtiene un usuario por ID"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, usuario_id, categoria_id, monto, fecha, descripcion, fecha_creacion, fecha_actualizacion
                FROM gastos 
                WHERE id = %s
            """
            cursor.execute(query, (gasto_id,))
            gasto = cursor.fetchone()

            return Gasto.model_validate(gasto) if gasto else None
            
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

    async def get_gasto_by_categoria_async(self, gasto_categoria: str) -> Optional[Gasto]:
        """Obtiene un Gasto por Categoria"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, usuario_id, categoria_id, monto, fecha, descripcion, fecha_creacion, fecha_actualizacion
                FROM gastos 
                WHERE categoria = %s
            """
            cursor.execute(query, (gasto_categoria,))
            gasto = cursor.fetchone()

            return Gasto.model_validate(gasto) if gasto else None
            
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

    async def create_gasto_async(self, gasto_data: GastoCreate) -> Optional[Gasto]:
        """Crea una nuevo gasto"""
        connection = self.db_config.get_connection()
        if not connection:
            raise Exception("No se pudo conectar a la base de datos")
        
        try:
            cursor = connection.cursor(dictionary=True)
            now = datetime.now()
            
            query = """
                INSERT INTO gastos (usuario_id, categoria_id, monto, fecha, descripcion, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                gasto_data.usuario_id,
                gasto_data.categoria_id,
                gasto_data.monto,
                now,
                gasto_data.descripcion,
                now
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            # Obtener la categoría recién creada
            gasto_id = cursor.lastrowid or -1
            return await self.get_gasto_by_id_async(gasto_id)
            
        except Error as e:
            connection.rollback()
            raise Exception(f"Error al crear categoría: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def update_gasto_async(self, gasto_id: int, gasto_data: GastoUpdate) -> Optional[Gasto]:
        """Actualiza un gasto existente"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            now = datetime.now()
            
            query = """
                UPDATE gastos 
                SET categoria_id = %s, monto = %s, fecha = %s, descripcion = %s, fecha_actualizacion = %s
                WHERE id = %s
            """
            values = (
                gasto_data.categoria_id,
                gasto_data.monto,
                gasto_data.fecha,
                gasto_data.descripcion,
                now,
                gasto_id
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            if cursor.rowcount > 0:
                return await self.get_gasto_by_id_async(gasto_id)
            return None
            
        except Error as e:
            connection.rollback()
            print(f"Error al actualizar categoría: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def delete_gasto_async(self, gasto_id: int) -> bool:
        """Elimina una categoría"""
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # # Verificar si hay gastos asociados a esta categoría
            # check_query = "SELECT COUNT(*) as count FROM gastos WHERE id = %s"
            # cursor.execute(check_query, (gasto_id,))
            # row = cast(Tuple[Any, ...], cursor.fetchone())
            # result = row[0]
            
            # if result > 0:
            #     raise Exception("No se puede eliminar la categoría porque tiene gastos asociados")
            
            # Eliminar la categoría
            delete_query = "DELETE FROM gastos WHERE id = %s"
            cursor.execute(delete_query, (gasto_id,))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()