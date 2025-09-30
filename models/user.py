import bcrypt
from utils.database import db

class User:
    def __init__(self, id=None, kullanici_adi=None, eposta=None, sifre_hash=None, 
                 adi_soyadi=None, profil_resmi=None, aktif=None, kayit_tarihi=None):
        self.id = id
        self.kullanici_adi = kullanici_adi
        self.eposta = eposta
        self.sifre_hash = sifre_hash
        self.adi_soyadi = adi_soyadi
        self.profil_resmi = profil_resmi
        self.aktif = aktif
        self.kayit_tarihi = kayit_tarihi
    
    @staticmethod
    def hash_password(password):
        """Şifreyi hash'ler"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def check_password(self, password):
        """Şifreyi kontrol eder"""
        try:
            if not self.sifre_hash:
                return False
                
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = self.sifre_hash.encode('utf-8')
            
            # Hash uzunluğunu kontrol et
            print(f"🔍 Şifre kontrolü: {self.kullanici_adi}")
            print(f"📏 Stored hash length: {len(self.sifre_hash)}")
            
            result = bcrypt.checkpw(password_bytes, stored_hash_bytes)
            print(f"✅ Şifre doğrulama sonucu: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Şifre kontrol hatası: {e}")
            return False
    
    @classmethod
    def get_by_username(cls, username):
        """Kullanıcı adına göre kullanıcı getirir"""
        query = "SELECT * FROM kullanici WHERE kullanici_adi = %s AND aktif = TRUE"
        result = db.execute_query(query, (username,), fetch=True)
        
        if result and len(result) > 0:
            user_data = result[0]
            print(f"✅ Kullanıcı verisi alındı: {user_data['kullanici_adi']}")
            return cls(**user_data)
        return None
    
    def to_dict(self):
        """Kullanıcı bilgilerini dictionary'ye çevirir"""
        return {
            'id': self.id,
            'kullanici_adi': self.kullanici_adi,
            'eposta': self.eposta,
            'adi_soyadi': self.adi_soyadi,
            'profil_resmi': self.profil_resmi,
            'aktif': bool(self.aktif),
            'kayit_tarihi': str(self.kayit_tarihi) if self.kayit_tarihi else None
        }