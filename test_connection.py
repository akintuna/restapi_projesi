import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='restdb',
        charset='utf8mb4'
    )
    
    print("✅ Bağlantı başarılı!")
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("📋 Tablolar:")
        for table in tables:
            # PyMySQL DictCursor kullanmıyorsak tuple döner
            print(f"  - {table[0]}")
            
except Exception as e:
    print(f"❌ Hata: {e}")
finally:
    if connection:
        connection.close()