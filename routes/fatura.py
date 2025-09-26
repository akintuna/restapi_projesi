from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.fatura import Fatura
from models.fatura_detay import FaturaDetay
from datetime import datetime
from utils.database import db

fatura_bp = Blueprint('fatura', __name__)

@fatura_bp.route('/api/fatura', methods=['GET'])
@jwt_required()
def get_faturalar():
    try:
        filters = {}
        if request.args.get('fatura_no'):
            filters['fatura_no'] = request.args.get('fatura_no')
        if request.args.get('cari_adi'):
            filters['cari_adi'] = request.args.get('cari_adi')
        if request.args.get('baslangic_tarihi'):
            filters['baslangic_tarihi'] = request.args.get('baslangic_tarihi')
        if request.args.get('bitis_tarihi'):
            filters['bitis_tarihi'] = request.args.get('bitis_tarihi')
        
        faturalar = Fatura.get_all(filters)
        
        return jsonify({
            'success': True,
            'data': [fatura.to_dict() for fatura in faturalar],
            'total': len(faturalar)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Fatura listeleme hatası: {str(e)}'}), 500

@fatura_bp.route('/api/fatura/<int:fatura_id>', methods=['GET'])
@jwt_required()
def get_fatura(fatura_id):
    try:
        fatura = Fatura.get_by_id(fatura_id)
        
        if not fatura:
            return jsonify({'error': 'Fatura bulunamadı'}), 404
        
        return jsonify({
            'success': True,
            'data': fatura.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Fatura getirme hatası: {str(e)}'}), 500

@fatura_bp.route('/api/fatura', methods=['POST'])
@jwt_required()
def create_fatura():
    try:
        data = request.get_json()
        
        # Validasyon
        if not data or not data.get('fatura_tarihi') or not data.get('cari_id'):
            return jsonify({'error': 'Fatura tarihi ve cari bilgisi gereklidir'}), 400
        
        if not data.get('detaylar') or len(data.get('detaylar', [])) == 0:
            return jsonify({'error': 'Fatura detayları gereklidir'}), 400
        
        print(f"🔧 Fatura Verisi: {data}")  # Debug
        
        # Detay hesaplamalarını yap
        for detay in data['detaylar']:
            totals = FaturaDetay.calculate_totals(
                detay['miktar'], 
                detay['birim_fiyat'], 
                detay['kdv_orani']
            )
            detay.update(totals)
        
        # Fatura oluştur
        yeni_fatura = Fatura(
            fatura_tarihi=data.get('fatura_tarihi'),
            fatura_no=data.get('fatura_no'),
            cari_id=data.get('cari_id'),
            aciklama=data.get('aciklama')
        )
        
        if yeni_fatura.create_with_details(data['detaylar']):
            # Oluşturulan faturayı tekrar getir (detayları ile)
            fatura_tam = Fatura.get_by_id(yeni_fatura.id)
            
            return jsonify({
                'success': True,
                'message': 'Fatura başarıyla oluşturuldu',
                'data': fatura_tam.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Fatura oluşturulamadı'}), 500
            
    except Exception as e:
        error_message = str(e)
        print(f"❌ Fatura oluşturma hatası: {error_message}")
        
        # MySQL hata kodlarına göre özelleştirilmiş mesajlar
        if "1062" in error_message and "fatura_no" in error_message:
            return jsonify({'error': 'Bu fatura numarası zaten kayıtlıdır'}), 400
        elif "foreign key" in error_message and "cari_id" in error_message:
            return jsonify({'error': 'Seçilen cari bulunamadı'}), 400
        elif "foreign key" in error_message and "urun_id" in error_message:
            return jsonify({'error': 'Seçilen ürün bulunamadı'}), 400
        else:
            return jsonify({'error': f'Fatura oluşturma hatası: {error_message}'}), 500

@fatura_bp.route('/api/fatura/<int:fatura_id>', methods=['DELETE'])
@jwt_required()
def delete_fatura(fatura_id):
    try:
        # Önce faturayı bul
        fatura = Fatura.get_by_id(fatura_id)
        if not fatura:
            return jsonify({'error': 'Fatura bulunamadı'}), 404
        
        # Transaction ile sil
        connection = db.get_connection()
        if not connection:
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
            
        cursor = None
        try:
            cursor = connection.cursor()
            
            # 1. Önce detayları sil
            cursor.execute("DELETE FROM fatura_detay WHERE fatura_id = %s", (fatura_id,))
            
            # 2. Sonra faturayı sil
            cursor.execute("DELETE FROM fatura WHERE id = %s", (fatura_id,))
            
            connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Fatura başarıyla silindi'
            }), 200
            
        except Exception as e:
            connection.rollback()
            return jsonify({'error': f'Fatura silme hatası: {str(e)}'}), 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            
    except Exception as e:
        return jsonify({'error': f'Fatura silme hatası: {str(e)}'}), 500

@fatura_bp.route('/api/fatura/hesapla', methods=['POST'])
@jwt_required()
def hesapla_detay():
    """Fatura detayı için hesaplama yapar"""
    try:
        data = request.get_json()
        
        miktar = float(data.get('miktar', 0))
        birim_fiyat = float(data.get('birim_fiyat', 0))
        kdv_orani = int(data.get('kdv_orani', 0))
        
        totals = FaturaDetay.calculate_totals(miktar, birim_fiyat, kdv_orani)
        
        return jsonify({
            'success': True,
            'data': totals
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Hesaplama hatası: {str(e)}'}), 500