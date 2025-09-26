import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Laragon şifresi
        database='restdb'
    )
    
    if connection.is_connected():
        print("✅ MySQL bağlantısı başarılı!")
        
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"📊 Bağlı veritabanı: {db_name[0]}")
        
        # Tabloları kontrol et
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("📋 Mevcut tablolar:")
        for table in tables:
            print(f"  - {table[0]}")
            
except Error as e:
    print(f"❌ Hata: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("🔌 Bağlantı kapatıldı")