from mysql.connector import Error
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.database import db_config
from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from typing import List, Optional, Tuple, Any, cast
from datetime import datetime, date
import bcrypt
from pydantic import BaseModel, EmailStr

class UsuarioService:

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def __init__(self):
        self.db_config = db_config

    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    async def get_all_usuarios_async(self) -> List[Usuario]:
        """Obtiene todos los usuarios"""
        connection = self.db_config.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, nombre, correo, password_hash, fecha_creacion, fecha_actualizacion
                FROM usuarios
            """
            cursor.execute(query)
            # Guardar resultados en variable local
            usuarios = cursor.fetchall()

            print(f"DEBUG - Total registros: {len(usuarios)}")
            # Use pydantic's model_validate to construct models from DB dicts
            return [Usuario.model_validate(usuario) for usuario in usuarios]
                
        except Error as e:
            print(f"Error al obtener usuarios: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def get_usuario_by_id_async(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, nombre, correo, password_hash, fecha_creacion, fecha_actualizacion
                FROM usuarios 
                WHERE id = %s
            """
            cursor.execute(query, (usuario_id,))
            usuario = cursor.fetchone()

            return Usuario.model_validate(usuario) if usuario else None
            
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

    async def get_usuario_by_nombre_async(self, usuario_nombre: str) -> Optional[Usuario]:
            """Obtiene un usuario por nombre"""
            connection = self.db_config.get_connection()
            if not connection:
                return None
        
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT id, nombre, correo, password_hash, fecha_creacion, fecha_actualizacion
                    FROM usuarios
                    WHERE nombre = %s
                """
                cursor.execute(query, (usuario_nombre))
                usuario = cursor.fetchone()

                return Usuario.model_validate(usuario) if usuario else None
            
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

    async def get_usuario_by_email_async(self, usuario_correo: EmailStr) -> Optional[Usuario]:
            """Obtiene un usuario por correo"""
            connection = self.db_config.get_connection()
            if not connection:
                return None
        
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT id, nombre, correo, fecha_creacion, fecha_actualizacion, password_hash
                    FROM usuarios
                    WHERE correo = %(correo)s
                """
                cursor.execute(query, {"correo": usuario_correo})
                usuario = cursor.fetchone()

                return Usuario.model_validate(usuario) if usuario else None
            
            except Error as e:
                print(f"Error al obtener el correo del usuario: {e}")
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
            
    async def create_usuario_async(self, usuario_data: UsuarioCreate) -> Optional[Usuario]:
        """Crea un nuevo usuario"""
        connection = self.db_config.get_connection()
        if not connection:
            raise Exception("No se pudo conectar a la base de datos")
        
        try:
            cursor = connection.cursor(dictionary=True)
            now = datetime.now()
            
            # Verificar si el correo ya existe
            existing_user = await self.get_usuario_by_email_async(usuario_data.correo)
            if existing_user:
                raise Exception("El correo ya está registrado")
            
            # Hashear contraseña
            hashed_password = self._hash_password(usuario_data.password)
            now = datetime.now()
            
            query = """
                INSERT INTO usuarios (nombre, correo, password_hash, fecha_creacion, fecha_actualizacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                usuario_data.nombre,
                usuario_data.correo,
                hashed_password,
                now,
                now
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            # Obtener el usuario recién creado
            usuario_id = cursor.lastrowid if cursor.lastrowid is not None else -1
            return await self.get_usuario_by_id_async(usuario_id)
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def update_usuario_async(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Optional[Usuario]:
        """Actualiza un usuario existente"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            now = datetime.now()
            
            # Construir query dinámicamente
            fields = []
            values = []
            
            if usuario_data.nombre is not None:
                fields.append("nombre = %s")
                values.append(usuario_data.nombre)
            if usuario_data.correo is not None:
                fields.append("correo = %s")
                values.append(usuario_data.correo)
                
            fields.append("fecha_actualizacion = %s")
            values.append(now)
            values.append(usuario_id)
            
            query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"
            cursor.execute(query, values)
            connection.commit()
            
            if cursor.rowcount > 0:
                return await self.get_usuario_by_id_async(usuario_id)
            return None
            
        except Error as e:
            connection.rollback()
            print(f"Error al actualizar usuario: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def delete_usuario_async(self, usuario_id: int) -> bool:
        """Elimina un usuario"""
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # Verificar si hay gastos asociados a este usuario
            check_query = "SELECT COUNT(*) as count FROM gastos WHERE usuario_id = %s"
            cursor.execute(check_query, (usuario_id,))
            row = cast(Tuple[Any, ...], cursor.fetchone())
            result = row[0]
            
            if result > 0:
                raise Exception("No se puede eliminar el usuario porque tiene gastos asociados")
            
            # Eliminar el usuario
            delete_query = "DELETE FROM usuarios WHERE id = %s"
            cursor.execute(delete_query, (usuario_id,))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
