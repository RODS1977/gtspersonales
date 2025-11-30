from models.categoria import Categoria
from utils.responses import success_response, error_response

class CategoriasService:
    @staticmethod
    def obtener_categorias():
        """
        Obtener todas las categorías
        """
        try:
            categorias = Categoria.obtener_todas()
            
            return success_response(
                message='Categorías obtenidas exitosamente',
                data=categorias,
                status_code=200
            )
        except Exception as e:
            return error_response(f'Error al obtener categorías: {str(e)}', status_code=500)

    @staticmethod
    def obtener_categoria_por_id(categoria_id):
        """
        Obtener categoría por ID
        """
        try:
            categoria = Categoria.obtener_por_id(categoria_id)
            
            if not categoria:
                return error_response('Categoría no encontrada', status_code=404)
            
            return success_response(
                message='Categoría obtenida exitosamente',
                data=categoria,
                status_code=200
            )
        except Exception as e:
            return error_response(f'Error al obtener categoría: {str(e)}', status_code=500)