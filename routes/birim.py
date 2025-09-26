from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.birim import Birim

birim_bp = Blueprint('birim', __name__)

@birim_bp.route('/api/birim', methods=['GET'])
@jwt_required()
def get_birimler():
    try:
        filters = {}
        if request.args.get('kisa_adi'):
            filters['kisa_adi'] = request.args.get('kisa_adi')
        if request.args.get('adi'):
            filters['adi'] = request.args.get('adi')
        
        birimler = Birim.get_all(filters)
        
        return jsonify({
            'success': True,
            'data': [birim.to_dict() for birim in birimler],
            'total': len(birimler)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Birim listeleme hatası: {str(e)}'}), 500

@birim_bp.route('/api/birim/<int:birim_id>', methods=['GET'])
@jwt_required()
def get_birim(birim_id):
    try:
        birim = Birim.get_by_id(birim_id)
        
        if not birim:
            return jsonify({'error': 'Birim bulunamadı'}), 404
        
        return jsonify({
            'success': True,
            'data': birim.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Birim getirme hatası: {str(e)}'}), 500

@birim_bp.route('/api/birim', methods=['POST'])
@jwt_required()
def create_birim():
    try:
        data = request.get_json()
        
        if not data or not data.get('adi'):
            return jsonify({'error': 'Birim adı gereklidir'}), 400
        
        yeni_birim = Birim(
            kisa_adi=data.get('kisa_adi'),
            adi=data.get('adi'),
            kg_karsiligi=data.get('kg_karsiligi', 1.0),
            aciklama=data.get('aciklama')
        )
        
        if yeni_birim.create():
            return jsonify({
                'success': True,
                'message': 'Birim başarıyla oluşturuldu',
                'data': yeni_birim.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Birim oluşturulamadı'}), 500
            
    except Exception as e:
        error_message = str(e)
        print(f"❌ Birim oluşturma hatası: {error_message}")
        
        if "1062" in error_message and "kisa_adi_adi" in error_message:
            return jsonify({'error': 'Bu birim adı veya kısa adı zaten kayıtlıdır'}), 400
        else:
            return jsonify({'error': f'Birim oluşturma hatası: {error_message}'}), 500

@birim_bp.route('/api/birim/<int:birim_id>', methods=['PUT'])
@jwt_required()
def update_birim(birim_id):
    try:
        data = request.get_json()
        
        birim = Birim.get_by_id(birim_id)
        if not birim:
            return jsonify({'error': 'Birim bulunamadı'}), 404
        
        if 'kisa_adi' in data:
            birim.kisa_adi = data['kisa_adi']
        if 'adi' in data:
            birim.adi = data['adi']
        if 'kg_karsiligi' in data:
            birim.kg_karsiligi = data['kg_karsiligi']
        if 'aciklama' in data:
            birim.aciklama = data['aciklama']
        
        if birim.update():
            return jsonify({
                'success': True,
                'message': 'Birim başarıyla güncellendi',
                'data': birim.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Birim güncellenemedi'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Birim güncelleme hatası: {str(e)}'}), 500

@birim_bp.route('/api/birim/<int:birim_id>', methods=['DELETE'])
@jwt_required()
def delete_birim(birim_id):
    try:
        birim = Birim.get_by_id(birim_id)
        if not birim:
            return jsonify({'error': 'Birim bulunamadı'}), 404
        
        if birim.delete():
            return jsonify({
                'success': True,
                'message': 'Birim başarıyla silindi'
            }), 200
        else:
            return jsonify({'error': 'Birim silinemedi'}), 500
            
    except Exception as e:
        error_msg = str(e)
        if "kullanımdadır" in error_msg:
            return jsonify({'error': error_msg}), 400
        return jsonify({'error': f'Birim silme hatası: {error_msg}'}), 500