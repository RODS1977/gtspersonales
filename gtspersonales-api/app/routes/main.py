from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root():
    return jsonify({
        "status": "success",
        "message": "API de Gastos Personales funcionando correctamente",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth/registro, /auth/login, /auth/logout",
            "gastos": "/api/gastos (GET, POST, PUT, DELETE)",
            "categorias": "/api/categorias"
        }
    })

@main_bp.route('/health')
def health_check():
    return jsonify({
        "status": "success",
        "message": "API saludable"
    })