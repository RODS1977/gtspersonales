# from pydantic import BaseModel, EmailStr
# from datetime import datetime
# from typing import Optional

# # class Usuario(BaseModel):
# #     id: int
# #     nombre: str
# #     correo: str
# #     password: str
# #     fecha_creacion: datetime
# #     fecha_actualizacion: datetime
# class UsuarioBase(BaseModel):
#     nombre: str
#     correo: EmailStr

# class UsuarioCreate(UsuarioBase):
#     password: str

# class UsuarioUpdate(BaseModel):
#     nombre: Optional[str] = None
#     correo: Optional[EmailStr] = None

# class Usuario(UsuarioBase):
#     id: int
#     fecha_creacion: Optional[datetime] = None
#     fecha_actualizacion: Optional[datetime] = None
#     password_hash: Optional[str] = None

#     class Config:
#         from_attributes = True

# class UsuarioLogin(BaseModel):
#     correo: EmailStr
#     password: str

from models.database import get_db_connection
import pymysql

class Usuario:
    @staticmethod
    def crear(nombre, correo, password_hash):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, correo, password_hash) VALUES (%s, %s, %s)",
                    (nombre, correo, password_hash)
                )
                usuario_id = cursor.lastrowid
                conn.commit()
                return usuario_id
        except pymysql.Error as e:
            print(f"Error al crear usuario: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_por_correo(correo):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, correo, password_hash FROM usuarios WHERE correo = %s",
                    (correo,)
                )
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error al obtener usuario por correo: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_por_id(usuario_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, correo, fecha_creacion FROM usuarios WHERE id = %s",
                    (usuario_id,)
                )
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error al obtener usuario por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def actualizar_password(usuario_id, nuevo_password_hash):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE usuarios SET password_hash = %s WHERE id = %s",
                    (nuevo_password_hash, usuario_id)
                )
                conn.commit()
                return True
        except pymysql.Error as e:
            print(f"Error al actualizar password: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()