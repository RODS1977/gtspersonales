from models.database import get_db_connection
from datetime import datetime
import pymysql

class TokenBlacklist:
    @staticmethod
    def revocar_token(jti, user_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO token_blacklist (jti, user_id, revoked_at) VALUES (%s, %s, %s)",
                    (jti, user_id, datetime.utcnow())
                )
                conn.commit()
                print(f"✅ Token revocado: {jti}")
        except pymysql.Error as e:
            print(f"❌ Error al revocar token: {e}")
            conn.rollback()
        finally:
            if conn:
                conn.close()

    @staticmethod
    def esta_revocado(jti):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT jti FROM token_blacklist WHERE jti = %s",
                    (jti,)
                )
                return cursor.fetchone() is not None
        except pymysql.Error as e:
            print(f"❌ Error al verificar token revocado: {e}")
            return False
        finally:
            if conn:
                conn.close()