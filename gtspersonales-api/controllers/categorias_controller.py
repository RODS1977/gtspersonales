from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.categoria import Categoria, CategoriaCreate, CategoriaUpdate
from services.categoria_service import CategoriaService
from idlelib.colorizer import DEBUG

router = APIRouter(prefix="/api/categorias", tags=["categorias"])

# Dependencia para el servicio
def get_categoria_service():
    return CategoriaService()

@router.get("/", response_model=List[Categoria])
async def get_all(service: CategoriaService = Depends(get_categoria_service)):
    return await service.get_all_categorias_async()

@router.get("/{id}", response_model=Categoria)
async def get_categoria_by_id_async(id: int, service: CategoriaService = Depends(get_categoria_service)):
    cat = await service.get_categoria_by_id_async(id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return cat

@router.get("/porNombre/{nombre}", response_model=Categoria)
async def get_categoria_by_nombre_async(nombre: str, service: CategoriaService = Depends(get_categoria_service)):
    cat = await service.get_categoria_by_nombre_async(nombre)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria por nombre no encontrado")
    return cat

@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    categoria_data: CategoriaCreate, 
    service: CategoriaService = Depends(get_categoria_service)
):
    try:
        print(f"DEBUG - categoria_data: {categoria_data}")
        return await service.create_categoria_async(categoria_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}", response_model=Categoria)
async def update_categoria(
    id: int, 
    categoria_data: CategoriaUpdate, 
    service: CategoriaService = Depends(get_categoria_service)
):
    print("El id de entrada es: %d", id)
    categoria = await service.update_categoria_async(id, categoria_data)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    return categoria

@router.delete("/{id}")
async def delete_categoria(
    id: int, 
    service: CategoriaService = Depends(get_categoria_service)
):
    try:
        success = await service.delete_categoria_async(id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        return {"message": "Categoría eliminada correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )