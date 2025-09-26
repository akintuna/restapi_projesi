import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # JWT Ayarları
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'restapi_projesi_icin_cok_gizli_anahtar_2025')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 saat
    
    # MySQL Bağlantı Ayarları - TÜRKÇE KARAKTERSİZ
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_USER = os.getenv('DB_USER', 'root')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', '')  # Boş şifre
    MYSQL_DB = os.getenv('DB_NAME', 'restdb')
    MYSQL_PORT = 3306
    
    # Sunucu Ayarları
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000