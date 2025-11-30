from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config

bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Habilitar CORS
    CORS(app)
    
    # Inicializar extensiones
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.gastos import gastos_bp
    from routes.categorias import categorias_bp
    from routes.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(gastos_bp, url_prefix='/api')
    app.register_blueprint(categorias_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    
    return app