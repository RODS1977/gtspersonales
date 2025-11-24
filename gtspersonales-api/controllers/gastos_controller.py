from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.gasto import Gasto, GastoCreate, GastoUpdate
from services.gasto_service import GastoService
from idlelib.colorizer import DEBUG
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/gastos", tags=["gastos"])

# Dependencia para el servicio
def get_gasto_service():
    return GastoService()

@router.get("/", response_model=List[Gasto])
async def get_all(service: GastoService = Depends(get_gasto_service)):
    return await service.get_all_gastos_async()

@router.get("/{id}", response_model=Gasto)
async def get_gasto_by_id_async(id: int, service: GastoService = Depends(get_gasto_service)):
    cat = await service.get_gasto_by_id_async(id)
    if not cat:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return cat

@router.get("/porCategoria/{categoria}", response_model=Gasto)
async def get_gasto_by_categoria_async(categoria: str, service: GastoService = Depends(get_gasto_service)):
    cat = await service.get_gasto_by_categoria_async(categoria)
    if not cat:
        raise HTTPException(status_code=404, detail="Gasto por categoria no encontrado")
    return cat

@router.post("/", response_model=Gasto, status_code=status.HTTP_201_CREATED)
async def create_gasto(
    gasto_data: GastoCreate, 
    service: GastoService = Depends(get_gasto_service)
):
    try:
        print(f"DEBUG - gasto_data: {gasto_data}")
        return await service.create_gasto_async(gasto_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}", response_model=Gasto)
async def update_gasto(
    id: int, 
    gasto_data: GastoUpdate, 
    service: GastoService = Depends(get_gasto_service)
):
    print("El id de entrada es: %d", id)
    gasto = await service.update_gasto_async(id, gasto_data)
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )
    return gasto

@router.delete("/{id}")
async def delete_gasto(
    id: int, 
    service: GastoService = Depends(get_gasto_service)
):
    try:
        success = await service.delete_gasto_async(id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto no encontrado"
            )
        return {"message": "Gasto eliminado correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )