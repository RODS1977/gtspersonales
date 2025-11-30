"""
Script de debug para la app de Gastos Personales
Ejecutar: python debug_app.py
"""

import sys
import os
import importlib

def verificar_imports():
    """Verificar que todos los imports funcionan"""
    print("🔍 VERIFICANDO IMPORTS...")
    
    imports_esenciales = [
        'app',
        'app.routes.auth',
        'app.routes.gastos', 
        'app.routes.categorias',
        'app.routes.main',
        'app.models.usuario',
        'app.models.gasto',
        'app.models.categoria',
        'app.models.token_blacklist',
        'app.services.auth_service',
        'app.services.gastos_service',
        'app.services.categorias_service',
        'app.utils.responses',
        'app.utils.validations'
    ]
    
    for modulo in imports_esenciales:
        try:
            importlib.import_module(modulo)
            print(f"✅ {modulo}")
        except ImportError as e:
            print(f"❌ {modulo}: {e}")
            return False
    
    return True

def verificar_base_datos():
    """Verificar conexión a base de datos"""
    print("\n🔍 VERIFICANDO BASE DE DATOS...")
    
    try:
        from models.database import get_db_connection
        conn = get_db_connection()
        if conn:
            print("✅ Conexión a BD exitosa")
            
            # Verificar tablas
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            print(f"✅ Tablas encontradas: {len(tablas)}")
            
            for tabla in tablas:
                print(f"   - {tabla[0]}")
            
            cursor.close()
            conn.close()
            return True
        else:
            print("❌ No se pudo conectar a BD")
            return False
            
    except Exception as e:
        print(f"❌ Error en BD: {e}")
        return False

def verificar_configuracion():
    """Verificar configuración de la app"""
    print("\n🔍 VERIFICANDO CONFIGURACIÓN...")
    
    try:
        from app import create_app
        app = create_app()
        
        config_checks = [
            ('SECRET_KEY', bool(app.config.get('SECRET_KEY'))),
            ('JWT_SECRET_KEY', bool(app.config.get('JWT_SECRET_KEY'))),
            ('DEBUG', app.config.get('DEBUG', False))
        ]
        
        for config_key, config_ok in config_checks:
            status = '✅' if config_ok else '❌'
            print(f"{status} {config_key}: {'OK' if config_ok else 'FALTANTE'}")
        
        return all(check[1] for check in config_checks)
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def main():
    """Función principal de debug"""
    print("🚀 INICIANDO DEBUG DE LA APP")
    print("=" * 50)
    
    # Verificar directorio
    if not os.path.exists('app'):
        print("❌ No estás en el directorio correcto")
        print("   Navega a: gastos-personales/")
        return
    
    checks = [
        verificar_imports(),
        verificar_base_datos(), 
        verificar_configuracion()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 ¡TODO CORRECTO! La app está lista.")
        print("\n📝 Para iniciar:")
        print("   (venv) python run.py")
    else:
        print("❌ Hay problemas que resolver antes de iniciar.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()