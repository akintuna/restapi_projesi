import bcrypt
from utils.database import db

def create_correct_user():
    # Önce mevcut kullanıcıyı sil
    db.execute_query("DELETE FROM kullanici WHERE kullanici_adi = 'admin'")
    
    # Şifreyi doğru şekilde hash'le
    password = "123456"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # Kullanıcıyı ekle
    query = """
    INSERT INTO kullanici (kullanici_adi, eposta, sifre_hash, adi_soyadi) 
    VALUES (%s, %s, %s, %s)
    """
    
    params = ('admin', 'admin@restapi.com', hashed_password.decode('utf-8'), 'Sistem Yoneticisi')
    
    result = db.execute_query(query, params)
    if result:
        print("✅ Kullanıcı başarıyla oluşturuldu!")
        print(f"📝 Kullanıcı Adı: admin")
        print(f"🔐 Şifre: 123456")
        print(f"🏷️ Hash: {hashed_password.decode('utf-8')}")
        
        # Kontrol et
        verify_password(hashed_password.decode('utf-8'), "123456")
    else:
        print("❌ Kullanıcı oluşturulamadı!")

def verify_password(stored_hash, password):
    """Şifreyi kontrol et"""
    try:
        password_bytes = password.encode('utf-8')
        stored_hash_bytes = stored_hash.encode('utf-8')
        is_valid = bcrypt.checkpw(password_bytes, stored_hash_bytes)
        print(f"🔍 Şifre kontrolü: {is_valid}")
        return is_valid
    except Exception as e:
        print(f"❌ Şifre kontrol hatası: {e}")
        return False

if __name__ == "__main__":
    create_correct_user()