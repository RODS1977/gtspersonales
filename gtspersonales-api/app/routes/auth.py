from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required as _jwt_required
from typing import Any, cast
# Cast jwt_required to Any to avoid partial/unknown typing from flask_jwt_extended stubs
jwt_required = cast(Any, _jwt_required)
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registro', methods=['POST'])
def registro():
    """
    Registrar nuevo usuario
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre
            - correo
            - password
          properties:
            nombre:
              type: string
              example: "Juan Pérez"
            correo:
              type: string
              example: "juan@ejemplo.com"
            password:
              type: string
              example: "Password123!"
    responses:
      201:
        description: Usuario registrado exitosamente
      400:
        description: Error en los datos de entrada
      500:
        description: Error interno del servidor
    """
    return AuthService.registrar_usuario(request.get_json())

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Iniciar sesión de usuario
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - correo
            - password
          properties:
            correo:
              type: string
              example: "juan@ejemplo.com"
            password:
              type: string
              example: "Password123!"
    responses:
      200:
        description: Login exitoso
      401:
        description: Credenciales inválidas
      400:
        description: Error en los datos de entrada
    """
    return AuthService.login_usuario(request.get_json())

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Cerrar sesión y revocar token
    ---
    tags:
      - Autenticación
    security:
      - Bearer: []
    responses:
      200:
        description: Sesión cerrada correctamente
      401:
        description: No autorizado
    """
    return AuthService.logout_usuario()

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Renovar token de acceso
    ---
    tags:
      - Autenticación
    security:
      - Bearer: []
    responses:
      200:
        description: Token renovado exitosamente
      401:
        description: Token inválido o expirado
    """
    return AuthService.refresh_token()

@auth_bp.route('/cambiar-password', methods=['POST'])
@jwt_required()
def cambiar_password():
    """
    Cambiar contraseña de usuario
    ---
    tags:
      - Autenticación
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - password_actual
            - nueva_password
          properties:
            password_actual:
              type: string
              example: "Password123!"
            nueva_password:
              type: string
              example: "NuevaPassword123!"
    responses:
      200:
        description: Contraseña cambiada exitosamente
      401:
        description: Contraseña actual incorrecta
      400:
        description: Error en los datos de entrada
    """
    return AuthService.cambiar_password(get_jwt_identity(), request.get_json())