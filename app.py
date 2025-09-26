from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import config

# Blueprint'leri import et
from routes.auth import auth_bp
from routes.cari import cari_bp
from routes.birim import birim_bp
from routes.urun import urun_bp
from routes.fatura import fatura_bp
from routes.web import web_bp  # YENİ EKLENDİ

def create_app():
    app = Flask(__name__)
    
    # Config yükleme
    app.config.from_object(config.Config)
    app.config['SECRET_KEY'] = 'web-panel-secret-key-2025'  # Session için
    
    # JWT ve CORS
    jwt = JWTManager(app)
    CORS(app)
    
    # Blueprint'leri kaydet
    app.register_blueprint(auth_bp)
    app.register_blueprint(cari_bp)
    app.register_blueprint(birim_bp)
    app.register_blueprint(urun_bp)
    app.register_blueprint(fatura_bp)
    app.register_blueprint(web_bp)  # YENİ EKLENDİ
    
    # Basit bir test endpoint'i
    @app.route('/api/test', methods=['GET'])
    def test():
        return jsonify({
            'status': 'success',
            'message': 'Flask API çalışıyor!',
            'version': '1.0.0'
        })
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=config.Config.HOST,
        port=config.Config.PORT,
        debug=config.Config.DEBUG
    )