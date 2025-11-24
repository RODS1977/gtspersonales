from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

# class Gasto(BaseModel):
#     id: int
#     usuario_id: int
#     categoria_id: int
#     monto: bool
#     fecha: datetime
#     descripcion: str
#     fecha_creacion: datetime
#     fecha_actualizacion: datetime

class GastoBase(BaseModel):
    usuario_id: int
    categoria_id: int
    monto: float
    fecha: date
    descripcion: Optional[str] = None

class GastoCreate(GastoBase):
    pass

class GastoUpdate(BaseModel):
    categoria_id: Optional[int] = None
    monto: Optional[float] = None
    fecha: Optional[date] = None
    descripcion: Optional[str] = None

class Gasto(GastoBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class GastoConRelaciones(Gasto):
    nombre_usuario: Optional[str] = None
    nombre_categoria: Optional[str] = None