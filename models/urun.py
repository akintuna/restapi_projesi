from utils.database import db

class Urun:
    def __init__(self, id=None, barkod=None, kisa_adi=None, adi=None, birim_id=None, kdv=None, aciklama=None, **kwargs):
        # **kwargs ekleyerek beklenmeyen parametreleri yakalıyoruz
        self.id = id
        self.barkod = barkod
        self.kisa_adi = kisa_adi
        self.adi = adi
        self.birim_id = birim_id
        self.kdv = int(kdv) if kdv else 0
        self.aciklama = aciklama
        
        # İlişkili veriler
        self.birim_adi = None

    @classmethod
    def get_all(cls, filters=None):
        """Tüm ürünleri getirir (birim bilgisi ile)"""
        query = """
        SELECT u.*, b.adi as birim_adi 
        FROM urun u 
        LEFT JOIN birim b ON u.birim_id = b.id 
        WHERE 1=1
        """
        params = []
        
        if filters:
            if filters.get('barkod'):
                query += " AND u.barkod LIKE %s"
                params.append(f"%{filters['barkod']}%")
            if filters.get('adi'):
                query += " AND u.adi LIKE %s"
                params.append(f"%{filters['adi']}%")
            if filters.get('kisa_adi'):
                query += " AND u.kisa_adi LIKE %s"
                params.append(f"%{filters['kisa_adi']}%")
        
        query += " ORDER BY u.adi"
        result = db.execute_query(query, params, fetch=True)
        
        if result:
            urunler = []
            for item in result:
                urun = cls(**item)
                urun.birim_adi = item.get('birim_adi')
                urunler.append(urun)
            return urunler
        return []
    
    @classmethod
    def get_by_id(cls, urun_id):
        """ID'ye göre ürün getirir"""
        query = """
        SELECT u.*, b.adi as birim_adi 
        FROM urun u 
        LEFT JOIN birim b ON u.birim_id = b.id 
        WHERE u.id = %s
        """
        result = db.execute_query(query, (urun_id,), fetch=True)
        
        if result and len(result) > 0:
            item = result[0]
            urun = cls(**item)
            urun.birim_adi = item.get('birim_adi')
            return urun
        return None
    
    def create(self):
        """Yeni ürün oluşturur"""
        query = "INSERT INTO urun (barkod, kisa_adi, adi, birim_id, kdv, aciklama) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (self.barkod, self.kisa_adi, self.adi, self.birim_id, self.kdv, self.aciklama)
        
        new_id = db.execute_query(query, params)
        if new_id:
            self.id = new_id
            return True
        return False
    
    def update(self):
        """Ürün günceller"""
        query = "UPDATE urun SET barkod = %s, kisa_adi = %s, adi = %s, birim_id = %s, kdv = %s, aciklama = %s WHERE id = %s"
        params = (self.barkod, self.kisa_adi, self.adi, self.birim_id, self.kdv, self.aciklama, self.id)
        
        result = db.execute_query(query, params)
        return result is not None
    
    def delete(self):
        """Ürün siler"""
        # Önce bu ürünü kullanan fatura detaylarını kontrol et
        check_query = "SELECT COUNT(*) as count FROM fatura_detay WHERE urun_id = %s"
        check_result = db.execute_query(check_query, (self.id,), fetch=True)
        
        if check_result and check_result[0]['count'] > 0:
            raise Exception("Bu ürün kullanımdadır, silinemez")
        
        query = "DELETE FROM urun WHERE id = %s"
        result = db.execute_query(query, (self.id,))
        return result is not None
    
    def to_dict(self):
        """Ürün bilgilerini dictionary'ye çevirir"""
        return {
            'id': self.id,
            'barkod': self.barkod,
            'kisa_adi': self.kisa_adi,
            'adi': self.adi,
            'birim_id': self.birim_id,
            'birim_adi': self.birim_adi,
            'kdv': self.kdv,
            'aciklama': self.aciklama
        }