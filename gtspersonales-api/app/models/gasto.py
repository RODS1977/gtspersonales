# from pydantic import BaseModel
# from datetime import datetime, date
# from typing import Optional

# # class Gasto(BaseModel):
# #     id: int
# #     usuario_id: int
# #     categoria_id: int
# #     monto: bool
# #     fecha: datetime
# #     descripcion: str
# #     fecha_creacion: datetime
# #     fecha_actualizacion: datetime

# class GastoBase(BaseModel):
#     usuario_id: int
#     categoria_id: int
#     monto: float
#     fecha: date
#     descripcion: Optional[str] = None

# class GastoCreate(GastoBase):
#     pass

# class GastoUpdate(BaseModel):
#     categoria_id: Optional[int] = None
#     monto: Optional[float] = None
#     fecha: Optional[date] = None
#     descripcion: Optional[str] = None

# class Gasto(GastoBase):
#     id: int
#     fecha_creacion: Optional[datetime] = None
#     fecha_actualizacion: Optional[datetime] = None

#     class Config:
#         from_attributes = True

# class GastoConRelaciones(Gasto):
#     nombre_usuario: Optional[str] = None
#     nombre_categoria: Optional[str] = None

from app.models.database import get_connection
import pymysql

class Gasto:
    @staticmethod
    def crear(usuario_id, categoria_id, monto, fecha, descripcion):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO gastos (usuario_id, categoria_id, monto, fecha, descripcion) VALUES (%s, %s, %s, %s, %s)",
                    (usuario_id, categoria_id, monto, fecha, descripcion)
                )
                gasto_id = cursor.lastrowid
                conn.commit()
                return gasto_id
        except pymysql.Error as e:
            print(f"Error al crear gasto: {e}")
            conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_por_usuario(usuario_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT g.id, c.nombre as categoria, g.monto, g.fecha, g.descripcion,
                           g.fecha_creacion, g.fecha_actualizacion
                    FROM gastos g
                    JOIN categorias c ON g.categoria_id = c.id
                    WHERE g.usuario_id = %s
                    ORDER BY g.fecha DESC, g.fecha_creacion DESC
                """, (usuario_id,))
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error al obtener gastos: {e}")
            return []
        finally:
            if conn:
                conn.close()
