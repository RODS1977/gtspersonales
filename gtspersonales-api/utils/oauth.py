from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import List, Optional, Tuple, Any, cast

from jose import JWTError, jwt
from models.token import TokenData
from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from services.usuario_service import UsuarioService


# --- Configuración ---
SECRET_KEY = "R0dr!goL4T!3n3MuyGord@"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Funciones auxiliares ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(service: UsuarioService, username: EmailStr) -> Optional[Usuario]:
    user = await service.get_usuario_by_email_async(username)
    if user != None:
        return user

async def authenticate_user(service: UsuarioService, username: EmailStr, password: str):
    user = await get_user(service, username)
    if not user:
        return False
    
    #print(user)
    #print("user.password_hash: %s", user.password_hash)

    #inputPassword = service._hash_password(password)
    #print("password after hash: %s", inputPassword)
    #if (user.password_hash != inputPassword):
    #    return False
    
    return user



    # if not verify_password(password, user.password_hash):
    #     return False
    #return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(service: UsuarioService, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: EmailStr = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(service, username=token_data.username or '')
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
        service: UsuarioService,
        current_user: Usuario = Depends(get_current_user)):
    #if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user