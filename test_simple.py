import pymysql

try:
    # Laragon default ayarları - şifre BOŞ
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # BOŞ ŞİFRE
        database='restdb',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("✅ Bağlantı başarılı!")
    
    with connection.cursor() as cursor:
        # DÜZELTİ: USER() fonksiyonu
        cursor.execute("SELECT USER() as current_user")
        user = cursor.fetchone()
        print(f"👤 Bağlı kullanıcı: {user['current_user']}")
        
        # Tabloları listele
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("📋 Mevcut tablolar:")
        for table in tables:
            table_name = list(table.values())[0]  # İlk değeri al
            print(f"  - {table_name}")
            
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'connection' in locals():
        connection.close()