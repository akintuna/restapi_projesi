from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.urun import Urun

urun_bp = Blueprint('urun', __name__)

@urun_bp.route('/api/urun', methods=['GET'])
@jwt_required()
def get_urunler():
    try:
        filters = {}
        if request.args.get('barkod'):
            filters['barkod'] = request.args.get('barkod')
        if request.args.get('adi'):
            filters['adi'] = request.args.get('adi')
        if request.args.get('kisa_adi'):
            filters['kisa_adi'] = request.args.get('kisa_adi')
        
        urunler = Urun.get_all(filters)
        
        return jsonify({
            'success': True,
            'data': [urun.to_dict() for urun in urunler],
            'total': len(urunler)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Ürün listeleme hatası: {str(e)}'}), 500

@urun_bp.route('/api/urun/<int:urun_id>', methods=['GET'])
@jwt_required()
def get_urun(urun_id):
    try:
        urun = Urun.get_by_id(urun_id)
        
        if not urun:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        return jsonify({
            'success': True,
            'data': urun.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Ürün getirme hatası: {str(e)}'}), 500

@urun_bp.route('/api/urun', methods=['POST'])
@jwt_required()
def create_urun():
    try:
        data = request.get_json()
        
        if not data or not data.get('adi'):
            return jsonify({'error': 'Ürün adı gereklidir'}), 400
        
        yeni_urun = Urun(
            barkod=data.get('barkod'),
            kisa_adi=data.get('kisa_adi'),
            adi=data.get('adi'),
            birim_id=data.get('birim_id'),
            kdv=data.get('kdv', 0),
            aciklama=data.get('aciklama')
        )
        
        if yeni_urun.create():
            return jsonify({
                'success': True,
                'message': 'Ürün başarıyla oluşturuldu',
                'data': yeni_urun.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Ürün oluşturulamadı'}), 500
            
    except Exception as e:
        error_message = str(e)
        print(f"❌ Ürün oluşturma hatası: {error_message}")
        
        if "1062" in error_message and "barkod" in error_message:
            return jsonify({'error': 'Bu barkod zaten kayıtlıdır'}), 400
        elif "1062" in error_message and "adi" in error_message:
            return jsonify({'error': 'Bu ürün adı zaten kayıtlıdır'}), 400
        elif "foreign key" in error_message and "birim_id" in error_message:
            return jsonify({'error': 'Seçilen birim bulunamadı'}), 400
        else:
            return jsonify({'error': f'Ürün oluşturma hatası: {error_message}'}), 500

@urun_bp.route('/api/urun/<int:urun_id>', methods=['PUT'])
@jwt_required()
def update_urun(urun_id):
    try:
        data = request.get_json()
        
        urun = Urun.get_by_id(urun_id)
        if not urun:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        if 'barkod' in data:
            urun.barkod = data['barkod']
        if 'kisa_adi' in data:
            urun.kisa_adi = data['kisa_adi']
        if 'adi' in data:
            urun.adi = data['adi']
        if 'birim_id' in data:
            urun.birim_id = data['birim_id']
        if 'kdv' in data:
            urun.kdv = data['kdv']
        if 'aciklama' in data:
            urun.aciklama = data['aciklama']
        
        if urun.update():
            return jsonify({
                'success': True,
                'message': 'Ürün başarıyla güncellendi',
                'data': urun.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Ürün güncellenemedi'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Ürün güncelleme hatası: {str(e)}'}), 500

@urun_bp.route('/api/urun/<int:urun_id>', methods=['DELETE'])
@jwt_required()
def delete_urun(urun_id):
    try:
        urun = Urun.get_by_id(urun_id)
        if not urun:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        if urun.delete():
            return jsonify({
                'success': True,
                'message': 'Ürün başarıyla silindi'
            }), 200
        else:
            return jsonify({'error': 'Ürün silinemedi'}), 500
            
    except Exception as e:
        error_msg = str(e)
        if "kullanımdadır" in error_msg:
            return jsonify({'error': error_msg}), 400
        return jsonify({'error': f'Ürün silme hatası: {error_msg}'}), 500