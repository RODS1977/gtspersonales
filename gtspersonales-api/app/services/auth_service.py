from flask import jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt,
)
from app.models.usuario import Usuario
from app.models.token_blacklist import TokenBlacklist
from app.utils.responses import success_response, error_response
from app.utils.validations import sanitizar_input, validar_correo_seguro
import re
import time
import secrets
from typing import Dict, Any, Tuple, Optional, List

class AuthService:
    # Lista de contraseñas comunes
    CONTRASEÑAS_COMUNES = [
        "password", "123456", "12345678", "123456789", "qwerty", 
        "contraseña", "password123", "admin", "welcome", "monkey"
    ]

    @staticmethod
    def registrar_usuario(data: Optional[Dict[str, Any]]) -> Tuple[Any, int]:
        """
        Registrar nuevo usuario con validaciones de seguridad mejoradas
        """
        try:
            # Validar que se recibieron datos
            if not data:
                return error_response('Datos JSON requeridos', status_code=400)
            
            # Sanitizar y extraer datos
            nombre = sanitizar_input(data.get('nombre', ''))
            correo = sanitizar_input(data.get('correo', '')).lower().strip()
            password = data.get('password', '')
            
            # Validaciones de campos obligatorios
            if not nombre:
                return error_response('El nombre es requerido', status_code=400)
            
            if not correo:
                return error_response('El correo electrónico es requerido', status_code=400)
            
            if not password:
                return error_response('La contraseña es requerida', status_code=400)
            
            # Validar formato de correo electrónico
            if not validar_correo_seguro(correo):
                return error_response('Formato de correo electrónico inválido o no permitido', status_code=400)
            
            # Validar longitud del nombre
            if len(nombre) < 2 or len(nombre) > 100:
                return error_response('El nombre debe tener entre 2 y 100 caracteres', status_code=400)
            
            # Validar fortaleza de contraseña
            es_valida, mensaje_error = AuthService.validar_fortaleza_password(password)
            if not es_valida:
                return error_response(mensaje_error, status_code=400)
            
            # Verificar si el correo ya existe
            usuario_existente = AuthService.verificar_usuario_existente(correo)
            if usuario_existente:
                return error_response('El correo electrónico ya está registrado', status_code=400)
            
            # Generar hash seguro de la contraseña
            password_hash = AuthService.generar_hash_seguro(password)
            
            # Crear usuario en la base de datos
            usuario_id = Usuario.crear(nombre, correo, password_hash)
            
            # Crear tokens de acceso
            access_token = create_access_token(identity=usuario_id)
            refresh_token = create_refresh_token(identity=usuario_id)
            
            # Preparar datos de respuesta
            user_data = {
                'id': usuario_id,
                'nombre': nombre,
                'correo': correo,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'nivel_seguridad': 'alto'
            }
            
            return success_response(
                message='Usuario registrado exitosamente.', 
                data=user_data, 
                status_code=201
            )
            
        except Exception as e:
            print(f"Error en registro: {str(e)}")
            return error_response('Error interno del servidor.', status_code=500)

    @staticmethod
    def login_usuario(data: Optional[Dict[str, Any]]) -> Tuple[Any, int]:
        """
        Iniciar sesión con protección contra timing attacks
        """
        try:
            # Validar que se recibieron datos
            if not data:
                return error_response('Datos JSON requeridos', status_code=400)
            
            # Sanitizar credenciales
            correo = sanitizar_input(data.get('correo', '')).lower().strip()
            password = data.get('password', '')
            
            # Validar campos obligatorios
            if not correo or not password:
                return error_response('Correo y contraseña son requeridos', status_code=400)
            
            # Verificación constante en el tiempo
            inicio = time.time()
            
            # Buscar usuario
            usuario = Usuario.obtener_por_correo(correo)
            
            if usuario:
                # Verificar contraseña con tiempo constante
                password_valido = check_password_hash(usuario['password_hash'], password)
            else:
                # Hash dummy para mantener tiempo constante
                dummy_hash = "$2b$14$fakestringfakestringfakestringfa"
                check_password_hash(dummy_hash, password)
                password_valido = False
            
            # Asegurar tiempo constante
            tiempo_transcurrido = (time.time() - inicio) * 1000
            if tiempo_transcurrido < 500:
                time.sleep((500 - tiempo_transcurrido) / 1000)
            
            if not password_valido:
                return error_response('Credenciales inválidas', status_code=401)
            
            # Crear tokens
            access_token = create_access_token(identity=usuario['id'])
            refresh_token = create_refresh_token(identity=usuario['id'])
            
            # Preparar datos de respuesta
            user_data = {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'correo': usuario['correo'],
                'access_token': access_token,
                'refresh_token': refresh_token,
                'ultimo_login': time.time()
            }
            
            return success_response(
                message='Login exitoso', 
                data=user_data, 
                status_code=200
            )
            
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return error_response('Error interno del servidor.', status_code=500)

    @staticmethod
    def logout_usuario() -> Tuple[Any, int]:
        """
        Cerrar sesión y revocar tokens
        """
        try:
            # Type hint explícito para get_jwt()
            jwt_data: Dict[str, Any] = get_jwt()
            jti = jwt_data['jti']
            user_id = get_jwt_identity()
            
            # Revocar token actual
            TokenBlacklist.revocar_token(jti, user_id)
            
            return success_response(
                message='Sesión cerrada correctamente.',
                status_code=200
            )
            
        except Exception as e:
            print(f"Error en logout: {str(e)}")
            return error_response('Error al cerrar sesión', status_code=500)

    @staticmethod
    def refresh_token() -> Tuple[Any, int]:
        """
        Renovar token de acceso
        """
        try:
            user_id = get_jwt_identity()
            
            # Verificar que el usuario aún existe
            usuario = Usuario.obtener_por_id(user_id)
            if not usuario:
                return error_response('Usuario no encontrado', status_code=404)
            
            # Crear nuevo token de acceso
            new_access_token = create_access_token(identity=user_id)
            
            return success_response(
                message='Token renovado exitosamente',
                data={'access_token': new_access_token},
                status_code=200
            )
            
        except Exception as e:
            print(f"Error renovando token: {str(e)}")
            return error_response('Error al renovar token', status_code=500)

    @staticmethod
    def validar_fortaleza_password(password: str) -> Tuple[bool, str]:
        """
        Validación robusta de fortaleza de contraseña
        """
        # Longitud mínima
        if len(password) < 12:
            return False, "La contraseña debe tener al menos 12 caracteres"
        
        # Verificar composición
        tiene_mayuscula = any(c.isupper() for c in password)
        tiene_minuscula = any(c.islower() for c in password)
        tiene_numero = any(c.isdigit() for c in password)
        tiene_especial = any(not c.isalnum() for c in password)
        
        if not all([tiene_mayuscula, tiene_minuscula, tiene_numero, tiene_especial]):
            return False, "Debe incluir mayúsculas, minúsculas, números y caracteres especiales"
        
        # Verificar contraseñas comunes
        if password.lower() in AuthService.CONTRASEÑAS_COMUNES:
            return False, "La contraseña es demasiado común y vulnerable"
        
        return True, "Contraseña válida"

    @staticmethod
    def generar_hash_seguro(password: str) -> str:
        """
        Generar hash seguro con configuración robusta
        """
        return generate_password_hash(password, rounds=14).decode('utf-8')

    @staticmethod
    def verificar_usuario_existente(correo: str) -> Optional[Dict[str, Any]]:
        """
        Verificar existencia de usuario
        """
        return Usuario.obtener_por_correo(correo)

    @staticmethod
    def cambiar_password(usuario_id: int, data: Dict[str, Any]) -> Tuple[Any, int]:
        """
        Cambiar contraseña de usuario
        """
        try:
            password_actual = data.get('password_actual')
            nueva_password = data.get('nueva_password')
            
            if not password_actual or not nueva_password:
                return error_response('Contraseña actual y nueva contraseña son requeridas', status_code=400)
            
            # Obtener usuario
            usuario = Usuario.obtener_por_id(usuario_id)
            if not usuario:
                return error_response('Usuario no encontrado', status_code=404)
            
            # Verificar contraseña actual
            if not check_password_hash(usuario['password_hash'], password_actual):
                return error_response('Contraseña actual incorrecta', status_code=401)
            
            # Validar nueva contraseña
            es_valida, mensaje_error = AuthService.validar_fortaleza_password(nueva_password)
            if not es_valida:
                return error_response(mensaje_error, status_code=400)
            
            # Verificar que no sea la misma contraseña
            if check_password_hash(usuario['password_hash'], nueva_password):
                return error_response('La nueva contraseña no puede ser igual a la actual', status_code=400)
            
            # Generar nuevo hash y actualizar
            nuevo_hash = AuthService.generar_hash_seguro(nueva_password)
            Usuario.actualizar_password(usuario_id, nuevo_hash)
            
            return success_response(
                message='Contraseña cambiada exitosamente',
                status_code=200
            )
            
        except Exception as e:
            print(f"Error cambiando password: {str(e)}")
            return error_response('Error al cambiar contraseña', status_code=500)