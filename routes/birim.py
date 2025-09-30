from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from models.birim import Birim

birim_bp = Blueprint('birim', __name__)

# ✅ API ROUTE'LARI

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
    


# ✅ WEB ARAYÜZÜ ROUTE'LARI

# BİRİM LİSTELEME (Web Arayüzü)
@birim_bp.route('/birimler')
def birim_listesi():
    try:
        # Filtreleme parametrelerini al
        filters = {}
        if request.args.get('adi'):
            filters['adi'] = request.args.get('adi')
        if request.args.get('kisa_adi'):
            filters['kisa_adi'] = request.args.get('kisa_adi')
        
        birimler = Birim.get_all(filters)
        return render_template('birimler.html', birimler=birimler)
    except Exception as e:
        flash(f'Birim listesi yüklenirken hata: {str(e)}', 'danger')
        return render_template('birimler.html', birimler=[])

# YENİ BİRİM EKLEME SAYFASI
@birim_bp.route('/birimler/yeni', methods=['GET', 'POST'])
def yeni_birim():
    try:
        if request.method == 'POST':
            # Form verilerini al
            kisa_adi = request.form.get('kisa_adi', '').strip()
            adi = request.form.get('adi', '').strip()
            aciklama = request.form.get('aciklama', '').strip()
            
            if not kisa_adi or not adi:
                flash('Kısa ad ve birim adı gereklidir!', 'danger')
                return render_template('birim_yeni.html')
            
            # Yeni birim oluştur
            yeni_birim = Birim(
                kisa_adi=kisa_adi,
                adi=adi,
                aciklama=aciklama
            )
            
            if yeni_birim.create():
                flash('Birim başarıyla oluşturuldu!', 'success')
                return redirect(url_for('birim.birim_listesi'))
            else:
                flash('Birim oluşturulamadı!', 'danger')
        
        return render_template('birim_yeni.html')
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('birim.birim_listesi'))

# BİRİM DÜZENLEME SAYFASI
@birim_bp.route('/birimler/<int:birim_id>/duzenle', methods=['GET', 'POST'])
def birim_duzenle(birim_id):
    try:
        birim = Birim.get_by_id(birim_id)
        
        if not birim:
            flash('Birim bulunamadı!', 'danger')
            return redirect(url_for('birim.birim_listesi'))
        
        if request.method == 'POST':
            # Form verilerini al
            birim.kisa_adi = request.form.get('kisa_adi', '').strip()
            birim.adi = request.form.get('adi', '').strip()
            birim.aciklama = request.form.get('aciklama', '').strip()
            
            # Güncelleme işlemi
            if birim.update():
                flash('Birim başarıyla güncellendi!', 'success')
                return redirect(url_for('birim.birim_listesi'))
            else:
                flash('Birim güncellenirken hata oluştu!', 'danger')
        
        return render_template('birim_duzenle.html', birim=birim)
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('birim.birim_listesi'))

# BİRİM SİLME
@birim_bp.route('/birimler/<int:birim_id>/sil', methods=['POST'])
def birim_sil(birim_id):
    try:
        birim = Birim.get_by_id(birim_id)
        if not birim:
            flash('Birim bulunamadı!', 'danger')
            return redirect(url_for('birim.birim_listesi'))
        
        if birim.delete():
            flash('Birim başarıyla silindi!', 'success')
        else:
            flash('Birim silinirken hata oluştu!', 'danger')
            
    except Exception as e:
        error_msg = str(e)
        if "kullanımdadır" in error_msg:
            flash('Bu birim kullanımdadır, önce ilişkili ürünleri silin!', 'warning')
        else:
            flash(f'Hata: {error_msg}', 'danger')
    
    return redirect(url_for('birim.birim_listesi'))

# BİRİM DETAY GÖRÜNTÜLEME
@birim_bp.route('/birimler/<int:birim_id>')
def birim_detay(birim_id):
    try:
        birim = Birim.get_by_id(birim_id)
        if not birim:
            flash('Birim bulunamadı!', 'danger')
            return redirect(url_for('birim.birim_listesi'))
        
        return render_template('birim_detay.html', birim=birim)
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('birim.birim_listesi'))
