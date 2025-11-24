
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# class Categoria(BaseModel):
#     id: int
#     nombre: str
#     descripcion: str
#     fecha_creacion: datetime

####################

class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
