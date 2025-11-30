from flask import jsonify
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

def success_response(
    message: str, 
    data: Optional[Any] = None, 
    status_code: int = 200,
    **additional_fields
) -> tuple:
    """
    Crear una respuesta de éxito estandarizada
    
    Args:
        message (str): Mensaje descriptivo del resultado
        data (Any, optional): Datos a incluir en la respuesta
        status_code (int, optional): Código HTTP de estado
        **additional_fields: Campos adicionales para la respuesta
    
    Returns:
        tuple: (JSON response, status code)
    """
    response: Dict[str, Any] = {
        'status': 'success',
        'message': message,
        'timestamp': get_current_timestamp()
    }
    
    if data is not None:
        response['data'] = data
    
    # Agregar campos adicionales si existen
    if additional_fields:
        response.update(additional_fields)
    
    return jsonify(response), status_code

def error_response(
    message: str, 
    errors: Optional[List[str]] = None, 
    status_code: int = 400,
    error_type: Optional[str] = None,
    **additional_fields
) -> tuple:
    """
    Crear una respuesta de error estandarizada
    
    Args:
        message (str): Mensaje descriptivo del error
        errors (List[str], optional): Lista de errores específicos
        status_code (int, optional): Código HTTP de estado
        error_type (str, optional): Tipo de error para categorización
        **additional_fields: Campos adicionales para la respuesta
    
    Returns:
        tuple: (JSON response, status code)
    """
    response: Dict[str, Any] = {
        'status': 'error',
        'message': message,
        'timestamp': get_current_timestamp()
    }
    
    if error_type:
        response['error_type'] = error_type
    
    if errors is not None:
        response['errors'] = errors
    
    # Agregar campos adicionales si existen
    if additional_fields:
        response.update(additional_fields)
    
    return jsonify(response), status_code

def validation_error_response(
    errors: List[str],
    message: str = "Errores de validación en los datos proporcionados"
) -> tuple:
    """
    Crear una respuesta de error de validación específica
    
    Args:
        errors (List[str]): Lista de errores de validación
        message (str, optional): Mensaje general de error
    
    Returns:
        tuple: (JSON response, status code 400)
    """
    return error_response(
        message=message,
        errors=errors,
        status_code=400,
        error_type='validation_error'
    )

def not_found_response(
    resource: str = "Recurso",
    resource_id: Optional[Any] = None
) -> tuple:
    """
    Crear una respuesta de recurso no encontrado
    
    Args:
        resource (str): Nombre del recurso no encontrado
        resource_id (Any, optional): ID del recurso no encontrado
    
    Returns:
        tuple: (JSON response, status code 404)
    """
    message = f"{resource} no encontrado"
    if resource_id is not None:
        message += f" (ID: {resource_id})"
    
    return error_response(
        message=message,
        status_code=404,
        error_type='not_found'
    )

def unauthorized_response(
    message: str = "No autorizado para acceder a este recurso"
) -> tuple:
    """
    Crear una respuesta de no autorizado
    
    Args:
        message (str, optional): Mensaje de error
    
    Returns:
        tuple: (JSON response, status code 401)
    """
    return error_response(
        message=message,
        status_code=401,
        error_type='unauthorized'
    )

def forbidden_response(
    message: str = "No tiene permisos para realizar esta acción"
) -> tuple:
    """
    Crear una respuesta de prohibido (sin permisos)
    
    Args:
        message (str, optional): Mensaje de error
    
    Returns:
        tuple: (JSON response, status code 403)
    """
    return error_response(
        message=message,
        status_code=403,
        error_type='forbidden'
    )

def internal_error_response(
    message: str = "Error interno del servidor",
    include_debug_info: bool = False,
    debug_info: Optional[str] = None
) -> tuple:
    """
    Crear una respuesta de error interno del servidor
    
    Args:
        message (str, optional): Mensaje de error
        include_debug_info (bool, optional): Incluir información de debug
        debug_info (str, optional): Información específica de debug
    
    Returns:
        tuple: (JSON response, status code 500)
    """
    response_data: Dict[str, Any] = {
        'message': message,
        'status_code': 500,
        'error_type': 'internal_server_error'
    }
    
    # Solo incluir info de debug en desarrollo
    if include_debug_info and debug_info:
        response_data['debug_info'] = debug_info
    
    return error_response(**response_data)

def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    per_page: int,
    message: str = "Datos obtenidos exitosamente"
) -> tuple:
    """
    Crear una respuesta paginada estandarizada
    
    Args:
        data (List[Any]): Lista de elementos de la página actual
        total (int): Total de elementos disponibles
        page (int): Página actual
        per_page (int): Elementos por página
        message (str, optional): Mensaje descriptivo
    
    Returns:
        tuple: (JSON response, status code 200)
    """
    total_pages = (total + per_page - 1) // per_page  # Cálculo de páginas totales
    
    pagination_info: Dict[str, Any] = {
        'data': data,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return success_response(
        message=message,
        data=pagination_info,
        status_code=200
    )

def get_current_timestamp() -> str:
    """
    Obtener timestamp actual en formato ISO
    
    Returns:
        str: Timestamp en formato ISO
    """
    return datetime.utcnow().isoformat() + 'Z'

# Alias para mantener compatibilidad con código existente
def jsonify_success(message: str, data: Optional[Any] = None, status_code: int = 200) -> tuple:
    return success_response(message, data, status_code)

def jsonify_error(message: str, errors: Optional[List[str]] = None, status_code: int = 400) -> tuple:
    return error_response(message, errors, status_code)

def jsonify_validation_error(errors: List[str]) -> tuple:
    return validation_error_response(errors)

# Respuestas específicas para la API de Gastos
def gasto_creado_response(gasto_data: Dict[str, Any]) -> tuple:
    """
    Respuesta específica para gasto creado exitosamente
    """
    return success_response(
        message='Gasto creado exitosamente',
        data=gasto_data,
        status_code=201
    )

def gasto_actualizado_response(gasto_data: Dict[str, Any]) -> tuple:
    """
    Respuesta específica para gasto actualizado exitosamente
    """
    return success_response(
        message='Gasto actualizado exitosamente',
        data=gasto_data,
        status_code=200
    )

def gasto_eliminado_response(gasto_data: Dict[str, Any]) -> tuple:
    """
    Respuesta específica para gasto eliminado exitosamente
    """
    return success_response(
        message='Gasto eliminado exitosamente',
        data={'gasto_eliminado': gasto_data},
        status_code=200
    )

def usuario_registrado_response(usuario_data: Dict[str, Any]) -> tuple:
    """
    Respuesta específica para usuario registrado exitosamente
    """
    return success_response(
        message='Usuario registrado exitosamente',
        data=usuario_data,
        status_code=201
    )

def login_exitoso_response(usuario_data: Dict[str, Any]) -> tuple:
    """
    Respuesta específica para login exitoso
    """
    return success_response(
        message='Login exitoso',
        data=usuario_data,
        status_code=200
    )

# Exportar todas las funciones
__all__ = [
    'success_response',
    'error_response',
    'validation_error_response',
    'not_found_response',
    'unauthorized_response',
    'forbidden_response',
    'internal_error_response',
    'paginated_response',
    'get_current_timestamp',
    'jsonify_success',
    'jsonify_error',
    'jsonify_validation_error',
    'gasto_creado_response',
    'gasto_actualizado_response',
    'gasto_eliminado_response',
    'usuario_registrado_response',
    'login_exitoso_response'
]