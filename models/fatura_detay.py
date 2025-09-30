from utils.database import db

class FaturaDetay:
    def __init__(self, id=None, fatura_id=None, urun_id=None, miktar=None, birim_id=None,
                 birim_fiyat=None, kdv_orani=None, brut_tutar=None, net_tutar=None, aciklama=None, **kwargs):
        # **kwargs ekleyerek beklenmeyen parametreleri yakalıyoruz
        self.id = id
        self.fatura_id = fatura_id
        self.urun_id = urun_id
        self.miktar = float(miktar) if miktar else 0.0
        self.birim_id = birim_id
        self.birim_fiyat = float(birim_fiyat) if birim_fiyat else 0.0
        self.kdv_orani = int(kdv_orani) if kdv_orani else 0
        self.brut_tutar = float(brut_tutar) if brut_tutar else 0.0
        self.net_tutar = float(net_tutar) if net_tutar else 0.0
        self.aciklama = aciklama
        
        # İlişkili veriler
        self.urun_adi = None
        self.birim_adi = None
    
    @classmethod
    def get_by_fatura_id(cls, fatura_id):
        """Fatura ID'ye göre detayları getirir"""
        query = """
        SELECT fd.*, u.adi as urun_adi, b.adi as birim_adi 
        FROM fatura_detay fd 
        LEFT JOIN urun u ON fd.urun_id = u.id 
        LEFT JOIN birim b ON fd.birim_id = b.id 
        WHERE fd.fatura_id = %s
        ORDER BY fd.id
        """
        result = db.execute_query(query, (fatura_id,), fetch=True)
        
        if result:
            detaylar = []
            for item in result:
                detay = cls(**item)  # **kwargs ile
                detay.urun_adi = item.get('urun_adi')  # Manuel atama
                detay.birim_adi = item.get('birim_adi')  # Manuel atama
                detaylar.append(detay)
            return detaylar
        return []
    
    @staticmethod
    def calculate_totals(miktar, birim_fiyat, kdv_orani):
        """Brut ve net tutarları hesaplar"""
        brut_tutar = miktar * birim_fiyat
        kdv_tutari = (brut_tutar * kdv_orani) / 100
        net_tutar = brut_tutar + kdv_tutari
        
        return {
            'brut_tutar': round(brut_tutar, 2),
            'net_tutar': round(net_tutar, 2)
        }
    
    def to_dict(self):
        """Detay bilgilerini dictionary'ye çevirir"""
        return {
            'id': self.id,
            'fatura_id': self.fatura_id,
            'urun_id': self.urun_id,
            'urun_adi': self.urun_adi,
            'miktar': float(self.miktar),
            'birim_id': self.birim_id,
            'birim_adi': self.birim_adi,
            'birim_fiyat': float(self.birim_fiyat),
            'kdv_orani': self.kdv_orani,
            'brut_tutar': float(self.brut_tutar),
            'net_tutar': float(self.net_tutar),
            'aciklama': self.aciklama
        }