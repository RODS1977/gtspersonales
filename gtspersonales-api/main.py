# from fastapi import FastAPI # type: ignore
# from passlib.context import CryptContext

# from controllers.categorias_controller import router as categoria_router
# from controllers.usuarios_controller import router as usuario_router
# from controllers.gastos_controller import router as gasto_router
# from controllers.token_controller import router as token_router



# app = FastAPI(
#     title="API de Gastos Personales",
#     description="API para gestión de Gastos Personales con MySQL",
#     version="0.0.1"
# )

# # Incluir rutas
# app.include_router(token_router)
# app.include_router(categoria_router)
# app.include_router(usuario_router)
# app.include_router(gasto_router)

# @app.get("/")
# async def root():
#     return {"message": "API funcionando correctamente"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from app import create_app
import os

app = create_app()

@app.route('/')
def root():
    return {"message": "API de Gastos Personales funcionando correctamente"}

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando servidor Flask en: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)