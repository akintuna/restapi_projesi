from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.cari import Cari

cari_bp = Blueprint('cari', __name__)

@cari_bp.route('/api/cari', methods=['GET'])
@jwt_required()
def get_cariler():
    try:
        # Filtreleme parametreleri
        filters = {}
        if request.args.get('adi_soyadi'):
            filters['adi_soyadi'] = request.args.get('adi_soyadi')
        if request.args.get('tc_kimlik_no'):
            filters['tc_kimlik_no'] = request.args.get('tc_kimlik_no')
        
        cariler = Cari.get_all(filters)
        
        return jsonify({
            'success': True,
            'data': [cari.to_dict() for cari in cariler],
            'total': len(cariler)
        }), 200
        
    except Exception as e:
        print(f"❌ Cari listeleme hatası: {e}")
        return jsonify({'error': f'Cari listeleme hatası: {str(e)}'}), 500

@cari_bp.route('/api/cari/<int:cari_id>', methods=['GET'])
@jwt_required()
def get_cari(cari_id):
    try:
        cari = Cari.get_by_id(cari_id)
        
        if not cari:
            return jsonify({'error': 'Cari bulunamadı'}), 404
        
        return jsonify({
            'success': True,
            'data': cari.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Cari getirme hatası: {str(e)}'}), 500

@cari_bp.route('/api/cari', methods=['POST'])
@jwt_required()
def create_cari():
    try:
        data = request.get_json()
        
        # Validasyon
        if not data or not data.get('adi_soyadi'):
            return jsonify({'error': 'Cari adı gereklidir'}), 400
        
        # Yeni cari oluştur
        yeni_cari = Cari(
            adi_soyadi=data.get('adi_soyadi'),
            tc_kimlik_no=data.get('tc_kimlik_no'),
            aciklama=data.get('aciklama')
        )
        
        # create() metodu artık exception fırlatabilir
        yeni_cari.create()
        
        return jsonify({
            'success': True,
            'message': 'Cari başarıyla oluşturuldu',
            'data': yeni_cari.to_dict()
        }), 201
            
    except Exception as e:
        # DETAYLI HATA MESAJI
        error_message = str(e)
        print(f"❌ Cari oluşturma hatası: {error_message}")
        
        # MySQL hata kodlarına göre özelleştirilmiş mesajlar
        if "1062" in error_message and "unq_adi" in error_message:
            return jsonify({'error': 'Bu cari adı zaten kayıtlıdır'}), 400
        elif "1062" in error_message and "tc_kimlik_no" in error_message:
            return jsonify({'error': 'Bu TC kimlik numarası zaten kayıtlıdır'}), 400
        elif "foreign key" in error_message.lower():
            return jsonify({'error': 'İlişkili kayıt hatası'}), 400
        else:
            # Genel hata mesajı
            return jsonify({'error': f'Cari oluşturulamadı: {error_message}'}), 500

@cari_bp.route('/api/cari/<int:cari_id>', methods=['PUT'])
@jwt_required()
def update_cari(cari_id):
    try:
        data = request.get_json()
        
        # Cari'yi bul
        cari = Cari.get_by_id(cari_id)
        if not cari:
            return jsonify({'error': 'Cari bulunamadı'}), 404
        
        # Güncelleme
        if 'adi_soyadi' in data:
            cari.adi_soyadi = data['adi_soyadi']
        if 'tc_kimlik_no' in data:
            cari.tc_kimlik_no = data['tc_kimlik_no']
        if 'aciklama' in data:
            cari.aciklama = data['aciklama']
        
        if cari.update():
            return jsonify({
                'success': True,
                'message': 'Cari başarıyla güncellendi',
                'data': cari.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Cari güncellenemedi'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Cari güncelleme hatası: {str(e)}'}), 500

@cari_bp.route('/api/cari/<int:cari_id>', methods=['DELETE'])
@jwt_required()
def delete_cari(cari_id):
    try:
        cari = Cari.get_by_id(cari_id)
        if not cari:
            return jsonify({'error': 'Cari bulunamadı'}), 404
        
        if cari.delete():
            return jsonify({
                'success': True,
                'message': 'Cari başarıyla silindi'
            }), 200
        else:
            return jsonify({'error': 'Cari silinemedi'}), 500
            
    except Exception as e:
        error_message = str(e)
        if "kullanımdadır" in error_message or "foreign key" in error_message:
            return jsonify({'error': 'Bu cari kullanımdadır, önce ilişkili faturaları silin'}), 400
        return jsonify({'error': f'Cari silme hatası: {error_message}'}), 500