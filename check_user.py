from utils.database import db

def check_existing_user():
    """Mevcut kullanıcıyı ve şifre hash'ini kontrol et"""
    query = "SELECT kullanici_adi, sifre_hash FROM kullanici WHERE kullanici_adi = 'admin'"
    result = db.execute_query(query, fetch=True)
    
    if result and len(result) > 0:
        user = result[0]
        print(f"👤 Kullanıcı: {user['kullanici_adi']}")
        print(f"🔐 Şifre Hash: {user['sifre_hash']}")
        print(f"📏 Hash Uzunluğu: {len(user['sifre_hash'])}")
    else:
        print("❌ Kullanıcı bulunamadı")

if __name__ == "__main__":
    check_existing_user()