from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from utils.database import db
import traceback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Kullanıcı adı ve şifre gereklidir'}), 400
        
        print(f"🔐 Login denemesi: {data['username']}")
        
        # Kullanıcıyı bul
        user = User.get_by_username(data['username'])
        if not user:
            print("❌ Kullanıcı bulunamadı")
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 401
        
        print(f"✅ Kullanıcı bulundu: {user.kullanici_adi}")
        
        # Şifreyi kontrol et
        is_valid_password = user.check_password(data['password'])
        print(f"🔑 Şifre kontrolü: {is_valid_password}")
        
        if not is_valid_password:
            return jsonify({'error': 'Geçersiz şifre'}), 401
        
        # JWT token oluştur
        access_token = create_access_token(identity=user.kullanici_adi)
        
        return jsonify({
            'success': True,
            'message': 'Giriş başarılı',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Giriş hatası: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Giriş hatası: {str(e)}'}), 500

@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_username = get_jwt_identity()
        user = User.get_by_username(current_username)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Kullanıcı bilgisi alınamadı: {str(e)}'}), 500

@auth_bp.route('/api/auth/test-db', methods=['GET'])

def test_db():
    """Veritabanı bağlantı testi"""
    try:
        result = db.execute_query("SELECT 1 as test", fetch=True)
        if result:
            return jsonify({'success': True, 'message': 'Veritabanı bağlantısı başarılı'})
        else:
            return jsonify({'error': 'Veritabanı bağlantısı başarısız'}), 500
    except Exception as e:
        return jsonify({'error': f'Veritabanı hatası: {str(e)}'}), 500