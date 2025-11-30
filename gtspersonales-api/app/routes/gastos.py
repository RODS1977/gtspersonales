from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.gasto_service import GastoService

gastos_bp = Blueprint('gastos', __name__)

@gastos_bp.route('/gastos', methods=['GET'])
@jwt_required()
def obtener_gastos():
    """
    Obtener todos los gastos del usuario autenticado
    ---
    tags:
      - Gastos
    security:
      - Bearer: []
    parameters:
      - in: query
        name: categoria
        required: false
        type: integer
        description: ID de categoría para filtrar
      - in: query
        name: mes
        required: false
        type: string
        description: Mes para filtrar (formato YYYY-MM)
    responses:
      200:
        description: Lista de gastos obtenida exitosamente
      401:
        description: No autorizado
      500:
        description: Error interno del servidor
    """
    usuario_id = get_jwt_identity()
    
    # Obtener parámetros de filtro
    categoria_id = request.args.get('categoria', type=int)
    mes = request.args.get('mes', type=str)
    
    filters = {}
    if categoria_id:
        filters['categoria_id'] = categoria_id
    if mes:
        filters['mes'] = mes
    
    return GastoService.obtener_gastos(usuario_id, filters)

@gastos_bp.route('/gastos', methods=['POST'])
@jwt_required()
def crear_gasto():
    """
    Crear un nuevo gasto
    ---
    tags:
      - Gastos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - categoria_id
            - monto
            - fecha
          properties:
            categoria_id:
              type: integer
              example: 1
            monto:
              type: number
              format: float
              example: 25.50
            fecha:
              type: string
              format: date
              example: "2024-01-15"
            descripcion:
              type: string
              example: "Almuerzo en restaurante"
    responses:
      201:
        description: Gasto creado exitosamente
      400:
        description: Error en los datos de entrada
      401:
        description: No autorizado
    """
    usuario_id = get_jwt_identity()
    return GastoService.create_gasto_async(usuario_id, request.get_json())

@gastos_bp.route('/gastos/<int:gasto_id>', methods=['GET'])
@jwt_required()
def obtener_gasto(gasto_id):
    """
    Obtener un gasto específico
    ---
    tags:
      - Gastos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: gasto_id
        required: true
        type: integer
        description: ID del gasto
    responses:
      200:
        description: Gasto obtenido exitosamente
      404:
        description: Gasto no encontrado
      401:
        description: No autorizado
    """
    usuario_id = get_jwt_identity()
    return GastoService.get_gasto_by_id_async(usuario_id, gasto_id)

@gastos_bp.route('/gastos/<int:gasto_id>', methods=['PUT'])
@jwt_required()
def actualizar_gasto(gasto_id):
    """
    Actualizar un gasto existente
    ---
    tags:
      - Gastos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: gasto_id
        required: true
        type: integer
        description: ID del gasto
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            categoria_id:
              type: integer
              example: 2
            monto:
              type: number
              format: float
              example: 30.00
            fecha:
              type: string
              format: date
              example: "2024-01-16"
            descripcion:
              type: string
              example: "Almuerzo actualizado"
    responses:
      200:
        description: Gasto actualizado exitosamente
      400:
        description: Error en los datos de entrada
      404:
        description: Gasto no encontrado
      401:
        description: No autorizado
    """
    usuario_id = get_jwt_identity()
    return GastoService.update_gasto_async(usuario_id, gasto_id, request.get_json())

@gastos_bp.route('/gastos/<int:gasto_id>', methods=['DELETE'])
@jwt_required()
def eliminar_gasto(gasto_id):
    """
    Eliminar un gasto
    ---
    tags:
      - Gastos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: gasto_id
        required: true
        type: integer
        description: ID del gasto
    responses:
      200:
        description: Gasto eliminado exitosamente
      404:
        description: Gasto no encontrado
      401:
        description: No autorizado
    """
    usuario_id = get_jwt_identity()
    return GastoService.delete_gasto_async(usuario_id, gasto_id)

@gastos_bp.route('/gastos/resumen', methods=['GET'])
@jwt_required()
def obtener_resumen():
    """
    Obtener resumen de gastos por categoría
    ---
    tags:
      - Gastos
    security:
      - Bearer: []
    parameters:
      - in: query
        name: mes
        required: false
        type: string
        description: Mes para el resumen (formato YYYY-MM)
    responses:
      200:
        description: Resumen obtenido exitosamente
      401:
        description: No autorizado
    """
    usuario_id = get_jwt_identity()
    mes = request.args.get('mes', type=str)
    
    return GastoService.obtener_resumen(usuario_id, mes)