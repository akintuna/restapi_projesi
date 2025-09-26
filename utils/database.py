import pymysql
from pymysql import Error
import config

class Database:
    def get_connection(self):
        """MySQL bağlantısı oluşturur"""
        try:
            connection = pymysql.connect(
                host=config.Config.MYSQL_HOST,
                user=config.Config.MYSQL_USER,
                password=config.Config.MYSQL_PASSWORD or '',
                database=config.Config.MYSQL_DB,
                port=config.Config.MYSQL_PORT,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Error as e:
            print(f"❌ MySQL bağlantı hatası: {e}")
            raise e  # Exception'ı yukarı fırlat
    
    def execute_query(self, query, params=None, fetch=False):
        """Sorgu çalıştırma yardımcı fonksiyonu - EXCEPTION FIRLATIR"""
        connection = self.get_connection()
        if connection is None:
            raise Exception("Veritabanı bağlantısı kurulamadı")
            
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
            else:
                connection.commit()
                result = cursor.lastrowid
            
            return result
            
        except Error as e:
            print(f"❌ Sorgu hatası: {e}")
            connection.rollback()
            raise e  # Exception'ı yukarı fırlat
        except Exception as e:
            print(f"❌ Genel sorgu hatası: {e}")
            connection.rollback()
            raise e  # Exception'ı yukarı fırlat
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Global database instance
db = Database()