from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# class Usuario(BaseModel):
#     id: int
#     nombre: str
#     correo: str
#     password: str
#     fecha_creacion: datetime
#     fecha_actualizacion: datetime
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None

class Usuario(UsuarioBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    password_hash: Optional[str] = None

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str