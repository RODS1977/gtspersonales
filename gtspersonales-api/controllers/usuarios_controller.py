from fastapi import APIRouter, Depends, HTTPException, status
from typing import List # type: ignore
from app.models.usuario import Usuario #UsuarioCreate, UsuarioUpdate
from app.services.usuario_service import UsuarioService
from idlelib.colorizer import DEBUG
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])

# Dependencia para el servicio
def get_usuario_service():
    return UsuarioService()

@router.get("/", response_model=List[Usuario])
async def get_all(service: UsuarioService = Depends(get_usuario_service)):
    return await service.get_all_usuarios_async()

@router.get("/{id}", response_model=Usuario)
async def get_usuario_by_id_async(id: int, service: UsuarioService = Depends(get_usuario_service)):
    cat = await service.get_usuario_by_id_async(id)
    if not cat:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return cat

@router.get("/porNombre/{nombre}", response_model=Usuario)
async def get_usuario_by_nombre_async(nombre:str, service: UsuarioService = Depends(get_usuario_service)):
    cat = await service.get_usuario_by_nombre_async(nombre)
    if not cat:
        raise HTTPException(status_code=404, detail="Usuario por nombre no encontrado")
    return cat

@router.get("/porCorreo/{correo}", response_model=Usuario)
async def get_usuario_by_email_async(correo:EmailStr, service: UsuarioService = Depends(get_usuario_service)):
    cat = await service.get_usuario_by_email_async(correo)
    if not cat:
        raise HTTPException(status_code=404, detail="Usuario por nombre no encontrado")
    return cat

@router.post("/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    usuario_data: UsuarioCreate, 
    service: UsuarioService = Depends(get_usuario_service)
):
    try:
        print(f"DEBUG - usuario_data: {usuario_data}")
        return await service.create_usuario_async(usuario_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}", response_model=Usuario)
async def update_usuario(
    id: int, 
    usuario_data: UsuarioUpdate, 
    service: UsuarioService = Depends(get_usuario_service)
):
    print("El id de entrada es: %d", id)
    usuario = await service.update_usuario_async(id, usuario_data)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrada"
        )
    return usuario

@router.delete("/{id}")
async def delete_usuario(
    id: int, 
    service: UsuarioService = Depends(get_usuario_service)
):
    try:
        success = await service.delete_usuario_async(id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrada"
            )
        return {"message": "Usuario eliminado correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )