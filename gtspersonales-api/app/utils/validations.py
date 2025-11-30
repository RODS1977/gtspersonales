import re
import html
from datetime import datetime
from typing import Union, Tuple, List, Optional, Dict, Any

def sanitizar_input(texto: Optional[str], max_length: int = 255) -> str:
    """
    Sanitizar entrada de texto para prevenir ataques XSS e inyección
    
    Args:
        texto (str): Texto a sanitizar
        max_length (int): Longitud máxima permitida
    
    Returns:
        str: Texto sanitizado
    """
    if texto is None:
        return ""
    
    # Convertir a string si no lo es
    texto = str(texto)
    
    # Eliminar espacios en blanco al inicio y final
    texto = texto.strip()
    
    # Escapar caracteres HTML
    texto = html.escape(texto)
    
    # Eliminar caracteres de control (excepto tab, newline, carriage return)
    texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texto)
    
    # Limitar longitud
    if len(texto) > max_length:
        texto = texto[:max_length]
    
    return texto

def validar_correo_seguro(correo: Optional[str]) -> bool:
    """
    Validación robusta de correo electrónico
    
    Args:
        correo (str): Correo a validar
    
    Returns:
        bool: True si el correo es válido y seguro
    """
    if not correo or len(correo) > 254:
        return False
    
    # Patrón básico de correo electrónico
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron, correo):
        return False
    
    # Prevenir correos temporales conocidos
    dominios_temporales = [
        'tempmail.com', '10minutemail.com', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'throwawaymail.com',
        'fakeinbox.com', 'trashmail.com', 'disposablemail.com'
    ]
    
    dominio = correo.split('@')[1].lower()
    if dominio in dominios_temporales:
        return False
    
    # Validar longitud de partes del correo
    partes = correo.split('@')
    if len(partes) != 2:
        return False
    
    local_part, domain_part = partes
    if len(local_part) > 64 or len(domain_part) > 253:
        return False
    
    return True

def validar_monto(monto: Optional[Union[int, float, str]]) -> bool:
    """
    Validar que el monto sea un número positivo
    
    Args:
        monto: Valor a validar
    
    Returns:
        bool: True si el monto es válido
    """
    try:
        if monto is None:
            return False
        
        # Convertir a float si es string
        if isinstance(monto, str):
            monto = float(monto)
        
        # Verificar que sea numérico y positivo
        return isinstance(monto, (int, float)) and monto > 0
    
    except (ValueError, TypeError):
        return False

def validar_fecha(fecha_str: Optional[str], formato: str = '%Y-%m-%d') -> bool:
    """
    Validar formato de fecha
    
    Args:
        fecha_str (str): Fecha en formato string
        formato (str): Formato esperado de la fecha
    
    Returns:
        bool: True si la fecha es válida
    """
    if not fecha_str:
        return False
    
    try:
        # Verificar formato
        fecha = datetime.strptime(fecha_str, formato)
        
        # Verificar que no sea fecha futura (para gastos)
        hoy = datetime.now()
        if fecha.date() > hoy.date():
            return False
        
        return True
    
    except ValueError:
        return False

def validar_descripcion(descripcion: Optional[str], max_length: int = 255) -> bool:
    """
    Validar descripción de gasto
    
    Args:
        descripcion (str): Descripción a validar
        max_length (int): Longitud máxima permitida
    
    Returns:
        bool: True si la descripción es válida
    """
    if descripcion is None:
        return True  # Descripción es opcional
    
    descripcion = str(descripcion)
    
    # Verificar longitud
    if len(descripcion) > max_length:
        return False
    
    # Verificar que no contenga caracteres peligrosos
    if re.search(r'[<>&\"\']', descripcion):
        return False
    
    return True

def validar_nombre(nombre: Optional[str]) -> Tuple[bool, str]:
    """
    Validar nombre de usuario
    
    Args:
        nombre (str): Nombre a validar
    
    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)
    """
    if not nombre:
        return False, "El nombre es requerido"
    
    nombre = nombre.strip()
    
    # Longitud
    if len(nombre) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    if len(nombre) > 100:
        return False, "El nombre no puede exceder 100 caracteres"
    
    # Caracteres permitidos (letras, espacios, algunos caracteres especiales)
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', nombre):
        return False, "El nombre contiene caracteres no permitidos"
    
    # Verificar que no sea solo espacios
    if not nombre.replace(' ', ''):
        return False, "El nombre no puede consistir solo de espacios"
    
    return True, "Nombre válido"

def validar_categoria_id(categoria_id: Optional[int], categorias_validas: Optional[List[int]] = None) -> bool:
    """
    Validar ID de categoría
    
    Args:
        categoria_id (int): ID de categoría a validar
        categorias_validas (list, optional): Lista de IDs válidos
    
    Returns:
        bool: True si el ID de categoría es válido
    """
    if not isinstance(categoria_id, int) or categoria_id <= 0:
        return False
    
    # Si se proporciona lista de categorías válidas, verificar contra ella
    if categorias_validas is not None:
        return categoria_id in categorias_validas
    
    return True

def validar_longitud_texto(texto: Optional[str], min_len: int = 0, max_len: int = 255) -> bool:
    """
    Validar longitud de texto genérico
    
    Args:
        texto (str): Texto a validar
        min_len (int): Longitud mínima permitida
        max_len (int): Longitud máxima permitida
    
    Returns:
        bool: True si la longitud es válida
    """
    if texto is None:
        texto = ""
    
    texto = str(texto)
    return min_len <= len(texto) <= max_len

def limpiar_y_validar_entrada(data: Optional[Dict[str, Any]], campos_requeridos: Optional[List[str]] = None) -> Tuple[Dict[str, Any], List[str]]:
    """
    Limpiar y validar múltiples campos de entrada
    
    Args:
        data (dict): Datos de entrada
        campos_requeridos (list, optional): Campos obligatorios
    
    Returns:
        Tuple[dict, list]: (datos_limpios, errores)
    """
    datos_limpios: Dict[str, Any] = {}
    errores: List[str] = []
    
    if data is None:
        data = {}
    
    # Validar campos requeridos
    if campos_requeridos:
        for campo in campos_requeridos:
            if campo not in data or data[campo] in [None, ""]:
                errores.append(f"El campo '{campo}' es requerido")
    
    # Limpiar todos los campos de texto
    for campo, valor in data.items():
        if isinstance(valor, str):
            datos_limpios[campo] = sanitizar_input(valor)
        else:
            datos_limpios[campo] = valor
    
    return datos_limpios, errores

# Exportar todas las funciones
__all__ = [
    'sanitizar_input',
    'validar_correo_seguro',
    'validar_monto',
    'validar_fecha',
    'validar_descripcion',
    'validar_nombre',
    'validar_categoria_id',
    'validar_longitud_texto',
    'limpiar_y_validar_entrada'
]