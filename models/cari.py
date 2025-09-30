from utils.database import db

class Cari:
    def __init__(self, id=None, adi_soyadi=None, tc_kimlik_no=None, aciklama=None):
        self.id = id
        self.adi_soyadi = adi_soyadi
        self.tc_kimlik_no = tc_kimlik_no
        self.aciklama = aciklama
    
    @classmethod
    def get_all(cls, filters=None):
        """Tüm carileri getirir (filtreleme desteği ile)"""
        try:
            query = "SELECT * FROM cari WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('adi_soyadi'):
                    query += " AND adi_soyadi LIKE %s"
                    params.append(f"%{filters['adi_soyadi']}%")
                if filters.get('tc_kimlik_no'):
                    query += " AND tc_kimlik_no LIKE %s"
                    params.append(f"%{filters['tc_kimlik_no']}%")
            
            query += " ORDER BY adi_soyadi"
            result = db.execute_query(query, params, fetch=True)
            
            if result:
                return [cls(**item) for item in result]
            return []
        except Exception as e:
            print(f"❌ Cari get_all hatası: {e}")
            return []
    
    @classmethod
    def get_by_id(cls, cari_id):
        """ID'ye göre cari getirir"""
        try:
            query = "SELECT * FROM cari WHERE id = %s"
            result = db.execute_query(query, (cari_id,), fetch=True)
            
            if result and len(result) > 0:
                return cls(**result[0])
            return None
        except Exception as e:
            print(f"❌ Cari get_by_id hatası: {e}")
            return None
    
    def create(self):
        """Yeni cari oluşturur - EXCEPTION FIRLATABİLİR"""
        query = "INSERT INTO cari (adi_soyadi, tc_kimlik_no, aciklama) VALUES (%s, %s, %s)"
        params = (self.adi_soyadi, self.tc_kimlik_no, self.aciklama)
        
        # execute_query exception fırlatabilir
        new_id = db.execute_query(query, params)
        self.id = new_id
        return True
    
    def update(self):
        """Cari günceller"""
        try:
            query = "UPDATE cari SET adi_soyadi = %s, tc_kimlik_no = %s, aciklama = %s WHERE id = %s"
            params = (self.adi_soyadi, self.tc_kimlik_no, self.aciklama, self.id)
            
            result = db.execute_query(query, params)
            return result is not None
        except Exception as e:
            print(f"❌ Cari update hatası: {e}")
            return False
    
    def delete(self):
        """Cari siler"""
        try:
            query = "DELETE FROM cari WHERE id = %s"
            result = db.execute_query(query, (self.id,))
            return result is not None
        except Exception as e:
            print(f"❌ Cari delete hatası: {e}")
            return False
    
    def to_dict(self):
        """Cari bilgilerini dictionary'ye çevirir"""
        return {
            'id': self.id,
            'adi_soyadi': self.adi_soyadi,
            'tc_kimlik_no': self.tc_kimlik_no,
            'aciklama': self.aciklama
        }