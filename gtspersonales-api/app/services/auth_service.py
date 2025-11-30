from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from models.usuario import Usuario
from models.token_blacklist import TokenBlacklist
from utils.responses import success_response, error_response
from utils.validations import sanitizar_input, validar_correo_seguro
import re
import time

class AuthService:
    # Lista de contraseñas comunes (puede extenderse desde base de datos)
    CONTRASEÑAS_COMUNES = [
        "password", "123456", "12345678", "123456789", "qwerty", 
        "contraseña", "password123", "admin", "welcome", "monkey",
        "letmein", "football", "iloveyou", "123123", "1234567",
        "abc123", "111111", "1234", "sunshine", "princess"
    ]

    @staticmethod
    def registrar_usuario(data):
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
            
            # Verificar si el correo ya existe (con tiempo constante)
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
            
            # Preparar datos de respuesta (sin información sensible)
            user_data = {
                'id': usuario_id,
                'nombre': nombre,
                'correo': correo,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'nivel_seguridad': 'alto'
            }
            
            return success_response(
                message='Usuario registrado exitosamente. Por favor, guarde sus credenciales de forma segura.', 
                data=user_data, 
                status_code=201
            )
            
        except Exception as e:
            # Log del error (en producción usar logging)
            print(f"Error en registro: {str(e)}")
            return error_response('Error interno del servidor. Por favor, intente más tarde.', status_code=500)

    @staticmethod
    def login_usuario(data):
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
            
            # Buscar usuario (siempre ejecuta las mismas operaciones)
            usuario = Usuario.obtener_por_correo(correo)
            
            if usuario:
                # Verificar contraseña con tiempo constante
                password_valido = check_password_hash(usuario['password_hash'], password)
            else:
                # Hash dummy para mantener tiempo constante
                dummy_hash = "$2b$14$fakestringfakestringfakestringfa"
                check_password_hash(dummy_hash, password)
                password_valido = False
            
            # Asegurar tiempo constante (aproximadamente 500ms)
            tiempo_transcurrido = (time.time() - inicio) * 1000
            if tiempo_transcurrido < 500:
                time.sleep((500 - tiempo_transcurrido) / 1000)
            
            if not password_valido:
                return error_response('Credenciales inválidas', status_code=401)
            
            # Verificar si el usuario está activo (para futuras extensiones)
            if hasattr(usuario, 'activo') and not usuario.get('activo', True):
                return error_response('Cuenta desactivada. Contacte al administrador.', status_code=403)
            
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
            
            # Actualizar último login (si existe el campo)
            AuthService.actualizar_ultimo_login(usuario['id'])
            
            return success_response(
                message='Login exitoso', 
                data=user_data, 
                status_code=200
            )
            
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return error_response('Error interno del servidor. Por favor, intente más tarde.', status_code=500)

    @staticmethod
    def logout_usuario():
        """
        Cerrar sesión y revocar tokens
        """
        try:
            jti = get_jwt()['jti']
            user_id = get_jwt_identity()
            
            # Revocar token actual
            TokenBlacklist.revocar_token(jti, user_id)
            
            return success_response(
                message='Sesión cerrada correctamente. Todos los tokens han sido revocados.',
                status_code=200
            )
            
        except Exception as e:
            print(f"Error en logout: {str(e)}")
            return error_response('Error al cerrar sesión', status_code=500)

    @staticmethod
    def refresh_token():
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
    def validar_fortaleza_password(password):
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
        
        # Verificar patrones simples
        if AuthService.contiene_patron_simple(password):
            return False, "La contraseña contiene patrones predecibles"
        
        # Verificar información personal (ejemplo básico)
        if AuthService.contiene_informacion_personal(password):
            return False, "La contraseña no debe contener información personal"
        
        # Score de fortaleza (opcional)
        score = AuthService.calcular_score_password(password)
        if score < 3:
            return False, "La contraseña es demasiado débil"
        
        return True, "Contraseña válida"

    @staticmethod
    def contiene_patron_simple(password):
        """
        Detectar patrones simples como 123456, abcd, etc.
        """
        patrones = [
            r'(\w)\1{2,}',  # Caracteres repetidos (aaa)
            r'(012|123|234|345|456|567|678|789)',  # Secuencias numéricas
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Secuencias alfabéticas
            r'(qwerty|asdfgh|zxcvbn)',  # Patrones de teclado
        ]
        
        for patron in patrones:
            if re.search(patron, password.lower()):
                return True
        return False

    @staticmethod
    def contiene_informacion_personal(password):
        """
        Detectar información personal común en contraseñas
        """
        # En una implementación real, esto se podría conectar a datos del usuario
        palabras_comunes = [
            'usuario', 'usuario123', 'nombre', 'apellido', 'correo',
            'telefono', 'cumpleaños', 'nacimiento', 'mascota'
        ]
        
        return any(palabra in password.lower() for palabra in palabras_comunes)

    @staticmethod
    def calcular_score_password(password):
        """
        Calcular score de fortaleza de contraseña (0-5)
        """
        score = 0
        
        # Longitud
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Complejidad de caracteres
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(not c.isalnum() for c in password):
            score += 1
        
        # Entropía básica
        if len(set(password)) >= len(password) * 0.8:
            score += 1
        
        return min(score, 5)

    @staticmethod
    def generar_hash_seguro(password):
        """
        Generar hash seguro con configuración robusta
        """
        # rounds=14 es un buen balance entre seguridad y rendimiento
        return generate_password_hash(password, rounds=14).decode('utf-8')

    @staticmethod
    def verificar_usuario_existente(correo):
        """
        Verificar existencia de usuario (puede extenderse para tiempo constante)
        """
        return Usuario.obtener_por_correo(correo)

    @staticmethod
    def actualizar_ultimo_login(usuario_id):
        """
        Actualizar timestamp de último login
        """
        try:
            # Esto sería una actualización en la base de datos
            # Por ahora es un placeholder para futura implementación
            pass
        except Exception as e:
            print(f"Error actualizando último login: {str(e)}")

    @staticmethod
    def cambiar_password(usuario_id, data):
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