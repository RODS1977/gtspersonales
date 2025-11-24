from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import List, Optional, Tuple, Any, cast

from jose import JWTError, jwt
from models.token import TokenData, Token
from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from services.usuario_service import UsuarioService
from utils.oauth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_active_user

router = APIRouter(prefix="/api/token", tags=["token"])

def get_usuario_service():
    return UsuarioService()

@router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UsuarioService = Depends(get_usuario_service)):
    user = await authenticate_user(service, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.correo}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/users/me", response_model=Usuario)
# async def read_users_me(
#     service: UsuarioService = Depends(get_usuario_service),
#     current_user: Usuario = Depends(get_current_active_user)):
#     return current_user