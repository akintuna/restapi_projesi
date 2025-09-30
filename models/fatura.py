from utils.database import db
from datetime import datetime
from models.fatura_detay import FaturaDetay

class Fatura:
    def __init__(self, id=None, fatura_tarihi=None, fatura_no=None, cari_id=None, 
                 toplam_miktar=None, toplam_kdv=None, toplam_tutar=None, aciklama=None, **kwargs):
        # **kwargs ekleyerek beklenmeyen parametreleri yakalıyoruz
        self.id = id
        self.fatura_tarihi = fatura_tarihi
        self.fatura_no = fatura_no
        self.cari_id = cari_id
        self.toplam_miktar = float(toplam_miktar) if toplam_miktar else 0.0
        self.toplam_kdv = float(toplam_kdv) if toplam_kdv else 0.0
        self.toplam_tutar = float(toplam_tutar) if toplam_tutar else 0.0
        self.aciklama = aciklama
        
        # İlişkili veriler
        self.cari_adi = None
        self.detaylar = []
    
    @classmethod
    def get_all(cls, filters=None):
        """Tüm faturaları getirir (cari bilgisi ile)"""
        query = """
        SELECT f.*, c.adi_soyadi as cari_adi 
        FROM fatura f 
        LEFT JOIN cari c ON f.cari_id = c.id 
        WHERE 1=1
        """
        params = []
        
        if filters:
            if filters.get('fatura_no'):
                query += " AND f.fatura_no LIKE %s"
                params.append(f"%{filters['fatura_no']}%")
            if filters.get('cari_adi'):
                query += " AND c.adi_soyadi LIKE %s"
                params.append(f"%{filters['cari_adi']}%")
            if filters.get('baslangic_tarihi'):
                query += " AND f.fatura_tarihi >= %s"
                params.append(filters['baslangic_tarihi'])
            if filters.get('bitis_tarihi'):
                query += " AND f.fatura_tarihi <= %s"
                params.append(filters['bitis_tarihi'])
        
        query += " ORDER BY f.fatura_tarihi DESC, f.id DESC"
        result = db.execute_query(query, params, fetch=True)
        
        if result:
            faturalar = []
            for item in result:
                fatura = cls(**item)  # Artık **kwargs ile cari_adi'yi handle ediyor
                fatura.cari_adi = item.get('cari_adi')  # Manuel olarak atıyoruz
                faturalar.append(fatura)
            return faturalar
        return []
    
    @classmethod
    def get_by_id(cls, fatura_id):
        """ID'ye göre faturayı ve detaylarını getirir"""
        # Fatura başlık bilgisi
        query = """
        SELECT f.*, c.adi_soyadi as cari_adi 
        FROM fatura f 
        LEFT JOIN cari c ON f.cari_id = c.id 
        WHERE f.id = %s
        """
        result = db.execute_query(query, (fatura_id,), fetch=True)
        
        if not result or len(result) == 0:
            return None
        
        item = result[0]
        fatura = cls(**item)  # **kwargs ile
        fatura.cari_adi = item.get('cari_adi')  # Manuel atama
        
        # Fatura detaylarını getir
        fatura.detaylar = FaturaDetay.get_by_fatura_id(fatura_id)
        
        return fatura
    
    def calculate_totals(self, detaylar):
        """Toplamları hesaplar"""
        toplam_miktar = 0.0
        toplam_brut = 0.0
        toplam_kdv = 0.0
        toplam_net = 0.0
        
        for detay in detaylar:
            toplam_miktar += detay['miktar']
            toplam_brut += detay['brut_tutar']
            toplam_kdv += (detay['brut_tutar'] * detay['kdv_orani'] / 100)
            toplam_net += detay['net_tutar']
        
        self.toplam_miktar = toplam_miktar
        self.toplam_kdv = toplam_kdv
        self.toplam_tutar = toplam_net
    
    def create_with_details(self, detaylar):
        """Faturayı ve detaylarını oluşturur (transaction)"""
        connection = db.get_connection()
        if not connection:
            return False
            
        cursor = None
        try:
            cursor = connection.cursor()
            
            # 1. Fatura numarası oluştur (basit bir yöntem)
            if not self.fatura_no:
                tarih = datetime.now().strftime("%Y%m%d")
                count_query = "SELECT COUNT(*) as count FROM fatura WHERE fatura_tarihi >= %s"
                count_result = db.execute_query(count_query, (f"{tarih[:4]}-{tarih[4:6]}-{tarih[6:8]}",), fetch=True)
                count = count_result[0]['count'] + 1 if count_result else 1
                self.fatura_no = f"FTR{tarih}{count:04d}"
            
            # 2. Toplamları hesapla
            self.calculate_totals(detaylar)
            
            # 3. Fatura başlığını ekle
            fatura_query = """
            INSERT INTO fatura (fatura_tarihi, fatura_no, cari_id, toplam_miktar, toplam_kdv, toplam_tutar, aciklama) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            fatura_params = (
                self.fatura_tarihi, self.fatura_no, self.cari_id, 
                self.toplam_miktar, self.toplam_kdv, self.toplam_tutar, self.aciklama
            )
            
            cursor.execute(fatura_query, fatura_params)
            fatura_id = cursor.lastrowid
            
            # 4. Fatura detaylarını ekle
            for detay in detaylar:
                detay_query = """
                INSERT INTO fatura_detay (fatura_id, urun_id, miktar, birim_id, birim_fiyat, kdv_orani, brut_tutar, net_tutar, aciklama) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                detay_params = (
                    fatura_id, detay['urun_id'], detay['miktar'], detay['birim_id'],
                    detay['birim_fiyat'], detay['kdv_orani'], detay['brut_tutar'], 
                    detay['net_tutar'], detay.get('aciklama', '')
                )
                cursor.execute(detay_query, detay_params)
            
            # 5. Commit transaction
            connection.commit()
            self.id = fatura_id
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"Fatura oluşturma hatası: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def to_dict(self):
        """Fatura bilgilerini dictionary'ye çevirir"""
        return {
            'id': self.id,
            'fatura_tarihi': str(self.fatura_tarihi) if self.fatura_tarihi else None,
            'fatura_no': self.fatura_no,
            'cari_id': self.cari_id,
            'cari_adi': self.cari_adi,
            'toplam_miktar': float(self.toplam_miktar),
            'toplam_kdv': float(self.toplam_kdv),
            'toplam_tutar': float(self.toplam_tutar),
            'aciklama': self.aciklama,
            'detaylar': [detay.to_dict() for detay in self.detaylar] if self.detaylar else []
        }