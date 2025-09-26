import bcrypt
from utils.database import db

def create_test_user():
    # Şifreyi hash'le
    password = "123456"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # SQL sorgusu
    query = """
    INSERT INTO kullanici (kullanici_adi, eposta, sifre_hash, adi_soyadi) 
    VALUES (%s, %s, %s, %s)
    """
    
    params = ('admin', 'admin@restapi.com', hashed_password.decode('utf-8'), 'Sistem Yoneticisi')
    
    result = db.execute_query(query, params)
    if result:
        print("✅ Test kullanıcısı başarıyla oluşturuldu!")
        print(f"Kullanıcı Adı: admin")
        print(f"Şifre: 123456")
    else:
        print("❌ Kullanıcı oluşturulamadı!")

if __name__ == "__main__":
    create_test_user()