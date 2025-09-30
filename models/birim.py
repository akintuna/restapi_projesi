from utils.database import db

class Birim:
    def __init__(self, id=None, kisa_adi=None, adi=None, kg_karsiligi=None, aciklama=None):
        self.id = id
        self.kisa_adi = kisa_adi
        self.adi = adi
        self.kg_karsiligi = float(kg_karsiligi) if kg_karsiligi else 1.0
        self.aciklama = aciklama
    
    @classmethod
    def get_all(cls, filters=None):
        """Tüm birimleri getirir"""
        query = "SELECT * FROM birim WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('kisa_adi'):
                query += " AND kisa_adi LIKE %s"
                params.append(f"%{filters['kisa_adi']}%")
            if filters.get('adi'):
                query += " AND adi LIKE %s"
                params.append(f"%{filters['adi']}%")
        
        query += " ORDER BY adi"
        result = db.execute_query(query, params, fetch=True)
        
        if result:
            return [cls(**item) for item in result]
        return []
    
    @classmethod
    def get_by_id(cls, birim_id):
        """ID'ye göre birim getirir"""
        query = "SELECT * FROM birim WHERE id = %s"
        result = db.execute_query(query, (birim_id,), fetch=True)
        
        if result and len(result) > 0:
            return cls(**result[0])
        return None
    
    def create(self):
        """Yeni birim oluşturur"""
        query = "INSERT INTO birim (kisa_adi, adi, kg_karsiligi, aciklama) VALUES (%s, %s, %s, %s)"
        params = (self.kisa_adi, self.adi, self.kg_karsiligi, self.aciklama)
        
        new_id = db.execute_query(query, params)
        if new_id:
            self.id = new_id
            return True
        return False
    
    def update(self):
        """Birim günceller"""
        query = "UPDATE birim SET kisa_adi = %s, adi = %s, kg_karsiligi = %s, aciklama = %s WHERE id = %s"
        params = (self.kisa_adi, self.adi, self.kg_karsiligi, self.aciklama, self.id)
        
        result = db.execute_query(query, params)
        return result is not None
    
    def delete(self):
        """Birim siler"""
        # Önce bu birimi kullanan ürünleri kontrol et
        check_query = "SELECT COUNT(*) as count FROM urun WHERE birim_id = %s"
        check_result = db.execute_query(check_query, (self.id,), fetch=True)
        
        if check_result and check_result[0]['count'] > 0:
            raise Exception("Bu birim kullanımdadır, silinemez")
        
        query = "DELETE FROM birim WHERE id = %s"
        result = db.execute_query(query, (self.id,))
        return result is not None
    
    def to_dict(self):
        """Birim bilgilerini dictionary'ye çevirir"""
        return {
            'id': self.id,
            'kisa_adi': self.kisa_adi,
            'adi': self.adi,
            'kg_karsiligi': float(self.kg_karsiligi) if self.kg_karsiligi else 1.0,
            'aciklama': self.aciklama
        }