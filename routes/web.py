from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
import requests
import json
from datetime import datetime  # YENİ EKLENDİ

web_bp = Blueprint('web', __name__)
API_BASE_URL = "http://localhost:5000"  # Base URL

def get_api_headers():
    """API istekleri için header'ları hazırla"""
    token = session.get('token')
    if token:
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    return {}

def make_api_request(method, endpoint, data=None):
    """API isteği yapan yardımcı fonksiyon - SADELEŞTİRİLMİŞ"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = get_api_headers()
        
        print(f"🔗 API İsteği: {method} {url}")
        
        if method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            # Diğer method'lar için basitçe
            response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📡 API Yanıt: {response.status_code}")
        print(f"🔍 MAKE_API_REQUEST: returning response, None")
        return response, None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Hatası: {e}")
        print(f"🔍 MAKE_API_REQUEST: returning None, error")
        return None, str(e)

def parse_api_error(response):
    """API'den gelen hata mesajını parse eder"""
    try:
        print(f"🔍 PARSE_API_ERROR: response status={response.status_code}")
        print(f"🔍 PARSE_API_ERROR: response text={response.text}")
        
        error_data = response.json()
        error_message = error_data.get('error', 'Bilinmeyen hata')
        
        print(f"🔍 PARSE_API_ERROR SONUÇ: '{error_message}'")
        
        return error_message
        
    except Exception as e:
        print(f"❌ PARSE_API_ERROR HATASI: {e}")
        return f"İşlem başarısız oldu (HTTP {response.status_code})"
    
@web_bp.route('/')
def index():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    # İstatistikleri API'den al - DÜZELTİLDİ
    stats = {}
    endpoints = [
        ('/api/cari', 'cariCount'),
        ('/api/urun', 'urunCount'), 
        ('/api/fatura', 'faturaCount'),
        ('/api/birim', 'birimCount')
    ]
    
    for endpoint, key in endpoints:
        response, error = make_api_request('GET', endpoint)
        if error:
            print(f"❌ {endpoint} hatası: {error}")
            stats[key] = 0
        elif response and response.status_code == 200:
            data = response.json()
            stats[key] = data.get('total', len(data.get('data', [])))
            print(f"✅ {endpoint}: {stats[key]} kayıt")
        else:
            print(f"❌ {endpoint} yanıt: {response.status_code if response else 'No response'}")
            stats[key] = 0
    
    return render_template('index.html', stats=stats)

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # API'ye login isteği gönder - DÜZELTİLDİ
        response, error = make_api_request('POST', '/api/auth/login', {
            'username': username,
            'password': password
        })
        
        if error:
            flash(f'Giriş hatası: {error}', 'danger')
        elif response and response.status_code == 200:
            data = response.json()
            session['token'] = data['access_token']
            session['user'] = data['user']
            flash('Başarıyla giriş yapıldı!', 'success')
            return redirect(url_for('web.index'))
        else:
            try:
                error_data = response.json()
                flash(f'Giriş başarısız: {error_data.get("error", "Bilinmeyen hata")}', 'danger')
            except:
                flash(f'Giriş başarısız! Status: {response.status_code}', 'danger')
    
    return render_template('login.html')

@web_bp.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yapıldı!', 'info')
    return redirect(url_for('web.login'))

# Cariler Sayfası - DÜZELTİLDİ
@web_bp.route('/cariler')
def cariler():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    response, error = make_api_request('GET', '/api/cari')
    if error:
        flash(error, 'danger')
        cariler = []
    elif response and response.status_code == 200:
        data = response.json()
        cariler = data.get('data', [])
        print(f"✅ Cariler yüklendi: {len(cariler)} kayıt")
    else:
        flash(f'Cariler yüklenemedi! Status: {response.status_code if response else "No response"}', 'danger')
        cariler = []
    
    return render_template('cariler.html', cariler=cariler)

# Ürünler Sayfası - DÜZELTİLDİ
@web_bp.route('/urunler')
def urunler():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    # Ürünleri getir
    response, error = make_api_request('GET', '/api/urun')
    if error:
        flash(error, 'danger')
        urunler = []
    elif response and response.status_code == 200:
        data = response.json()
        urunler = data.get('data', [])
        print(f"✅ Ürünler yüklendi: {len(urunler)} kayıt")
    else:
        flash(f'Ürünler yüklenemedi! Status: {response.status_code if response else "No response"}', 'danger')
        urunler = []
    
    # Birimleri getir (form için) - DÜZELTİLDİ
    birim_response, error = make_api_request('GET', '/api/birim')
    birimler = []
    
    if error:
        flash(f'Birimler yüklenirken hata: {error}', 'warning')
    elif birim_response and birim_response.status_code == 200:
        birim_data = birim_response.json()
        birimler = birim_data.get('data', [])
        print(f"✅ Birimler yüklendi: {len(birimler)} kayıt")
    else:
        flash('Birimler yüklenemedi!', 'warning')
    
    return render_template('urunler.html', urunler=urunler, birimler=birimler)

# Birimler Sayfası - DÜZELTİLDİ
@web_bp.route('/birimler')
def birimler():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    response, error = make_api_request('GET', '/api/birim')
    if error:
        flash(error, 'danger')
        birimler = []
    elif response and response.status_code == 200:
        data = response.json()
        birimler = data.get('data', [])
        print(f"✅ Birimler yüklendi: {len(birimler)} kayıt")
    else:
        flash(f'Birimler yüklenemedi! Status: {response.status_code if response else "No response"}', 'danger')
        birimler = []
    
    return render_template('birimler.html', birimler=birimler)

# Faturalar Sayfası - DÜZELTİLDİ
@web_bp.route('/faturalar')
def faturalar():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    # Faturaları getir
    response, error = make_api_request('GET', '/api/fatura')
    if error:
        flash(error, 'danger')
        faturalar = []
    elif response and response.status_code == 200:
        data = response.json()
        faturalar = data.get('data', [])
        print(f"✅ Faturalar yüklendi: {len(faturalar)} kayıt")
    else:
        flash(f'Faturalar yüklenemedi! Status: {response.status_code if response else "No response"}', 'danger')
        faturalar = []
    
    # Carileri getir (form için) - DÜZELTİLDİ
    cari_response, error = make_api_request('GET', '/api/cari')
    cariler = []
    if cari_response and cari_response.status_code == 200:
        cari_data = cari_response.json()
        cariler = cari_data.get('data', [])
        print(f"✅ Cariler yüklendi: {len(cariler)} kayıt")
    
    return render_template('faturalar.html', faturalar=faturalar, cariler=cariler)

# Yeni Cari Ekleme - DÜZELTİLDİ
@web_bp.route('/cariler/yeni', methods=['GET', 'POST'])
def yeni_cari():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    print(f"🔍 ROUTE BAŞLANGICI: method={request.method}")
    
    if request.method == 'POST':
        print("🔍 POST REQUEST TESPİT EDİLDİ")
        
        # Form verilerini al
        yeni_cari_data = {
            'adi_soyadi': request.form.get('adi_soyadi', '').strip(),
            'tc_kimlik_no': request.form.get('tc_kimlik_no', '').strip(),
            'aciklama': request.form.get('aciklama', '').strip()
        }
        
        print(f"🎯 FORM DATA: {yeni_cari_data}")
        
        # API çağrısı
        print("🔍 API ÇAĞRISI ÖNCESİ")
        api_response, api_error = make_api_request('POST', '/api/cari', yeni_cari_data)
        print(f"🔍 API ÇAĞRISI SONRASI: api_response={api_response}, api_error={api_error}")
        
        # DOĞRU IF-ELSE KOŞULLARI:
        if api_error is not None:
            print("❌ ERROR DURUMU")
            flash(f'Bağlantı hatası: {api_error}', 'danger')
        elif api_response is not None:
            print(f"✅ RESPONSE DURUMU: status_code={api_response.status_code}")
            if api_response.status_code == 201:
                print("🎉 BAŞARILI - 201")
                flash('Cari başarıyla eklendi!', 'success')
                return redirect(url_for('web.cariler'))
            else:
                print("⚠️ API HATASI - 400/500")
                error_message = parse_api_error(api_response)
                print(f"🔍 PARSE EDİLEN HATA: {error_message}")
                flash(f'Cari eklenemedi: {error_message}', 'danger')
        else:
            print("❓ BEKLENMEYEN DURUM - İKİSİ DE None")
            flash('Beklenmeyen bir hata oluştu!', 'danger')
        
        print("🔍 RENDER TEMPLATE ÖNCESİ")
        return render_template('yeni_cari.html', form_data=yeni_cari_data)
    
    print("🔍 GET REQUEST")
    return render_template('yeni_cari.html')

# Yeni Ürün Ekleme - DÜZELTİLDİ
@web_bp.route('/urunler/yeni', methods=['GET', 'POST'])
def yeni_urun():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    # Birimleri getir
    birim_response, birim_error = make_api_request('GET', '/api/birim')
    birimler = []
    
    if birim_error is not None:
        flash(f'Birimler yüklenirken hata: {birim_error}', 'warning')
    elif birim_response is not None and birim_response.status_code == 200:
        birim_data = birim_response.json()
        birimler = birim_data.get('data', [])
    
    if request.method == 'POST':
        yeni_urun_data = {
            'barkod': request.form.get('barkod', '').strip(),
            'kisa_adi': request.form.get('kisa_adi', '').strip(),
            'adi': request.form.get('adi', '').strip(),
            'birim_id': request.form.get('birim_id') or None,
            'kdv': int(request.form.get('kdv', 8)),
            'aciklama': request.form.get('aciklama', '').strip()
        }
        
        if not yeni_urun_data['adi']:
            flash('Ürün adı gereklidir!', 'danger')
            return render_template('yeni_urun.html', birimler=birimler, form_data=yeni_urun_data)
        
        api_response, api_error = make_api_request('POST', '/api/urun', yeni_urun_data)
        
        if api_error is not None:
            flash(f'Bağlantı hatası: {api_error}', 'danger')
        elif api_response is not None:
            if api_response.status_code == 201:
                flash('Ürün başarıyla eklendi!', 'success')
                return redirect(url_for('web.urunler'))
            else:
                error_message = parse_api_error(api_response)
                flash(f'Ürün eklenemedi: {error_message}', 'danger')
        else:
            flash('Beklenmeyen bir hata oluştu!', 'danger')
        
        return render_template('yeni_urun.html', birimler=birimler, form_data=yeni_urun_data)
    
    return render_template('yeni_urun.html', birimler=birimler)

# Yeni Birim Ekleme - DÜZELTİLDİ
@web_bp.route('/birimler/yeni', methods=['GET', 'POST'])
def yeni_birim():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    if request.method == 'POST':
        # Form verilerini al
        yeni_birim_data = {
            'kisa_adi': request.form.get('kisa_adi', '').strip(),
            'adi': request.form.get('adi', '').strip(),
            'kg_karsiligi': float(request.form.get('kg_karsiligi', 1.0)),
            'aciklama': request.form.get('aciklama', '').strip()
        }
        
        # Validasyon
        if not yeni_birim_data['kisa_adi']:
            flash('Birim kısa adı gereklidir!', 'danger')
            return render_template('yeni_birim.html', form_data=yeni_birim_data)
        
        if not yeni_birim_data['adi']:
            flash('Birim adı gereklidir!', 'danger')
            return render_template('yeni_birim.html', form_data=yeni_birim_data)
        
        # API'ye gönder - DÜZELTİLMİŞ VERSİYON
        api_response, api_error = make_api_request('POST', '/api/birim', yeni_birim_data)
        
        if api_error is not None:
            flash(f'Bağlantı hatası: {api_error}', 'danger')
        elif api_response is not None:
            if api_response.status_code == 201:
                flash('Birim başarıyla eklendi!', 'success')
                return redirect(url_for('web.birimler'))
            else:
                error_message = parse_api_error(api_response)
                flash(f'Birim eklenemedi: {error_message}', 'danger')
        else:
            flash('Beklenmeyen bir hata oluştu!', 'danger')
        
        return render_template('yeni_birim.html', form_data=yeni_birim_data)
    
    return render_template('yeni_birim.html')

# API Test Endpoint'i - DÜZELTİLDİ
@web_bp.route('/api-test')
def api_test():
    """API bağlantı testi"""
    if 'token' not in session:
        return jsonify({'error': 'Giriş yapılmamış'}), 401
    
    # Çeşitli endpoint'leri test et - DÜZELTİLDİ
    test_results = {}
    endpoints = ['/api/health', '/api/cari', '/api/urun', '/api/birim', '/api/fatura']
    
    for endpoint in endpoints:
        response, error = make_api_request('GET', endpoint)
        if error:
            test_results[endpoint] = {'status': 'error', 'message': error}
        elif response:
            test_results[endpoint] = {
                'status': 'success', 
                'status_code': response.status_code,
                'data_count': len(response.json().get('data', [])) if response.status_code == 200 else 0
            }
        else:
            test_results[endpoint] = {'status': 'error', 'message': 'No response'}
    
    return jsonify(test_results)


@web_bp.route('/faturalar/yeni', methods=['GET', 'POST'])
def yeni_fatura():
    if 'token' not in session:
        return redirect(url_for('web.login'))
    
    # Gerekli verileri getir
    cariler_response, cariler_error = make_api_request('GET', '/api/cari')
    urunler_response, urunler_error = make_api_request('GET', '/api/urun')
    birimler_response, birimler_error = make_api_request('GET', '/api/birim')
    
    cariler = []
    urunler = []
    birimler = []
    
    if cariler_response and cariler_response.status_code == 200:
        cariler = cariler_response.json().get('data', [])
    
    if urunler_response and urunler_response.status_code == 200:
        urunler = urunler_response.json().get('data', [])
    
    if birimler_response and birimler_response.status_code == 200:
        birimler = birimler_response.json().get('data', [])
    
    # Bugünün tarihi ve fatura no için hazırlık
    today = datetime.now().strftime('%Y-%m-%d')
    fatura_no = f"FTR{datetime.now().strftime('%Y%m%d')}001"
    
    if request.method == 'POST':
        # Form verilerini al
        fatura_data = {
            'fatura_tarihi': request.form.get('fatura_tarihi'),
            'fatura_no': request.form.get('fatura_no'),
            'cari_id': request.form.get('cari_id'),
            'aciklama': request.form.get('aciklama', '')
        }
        
        # Detayları JSON'dan parse et
        try:
            detaylar_json = request.form.get('detaylar', '[]')
            fatura_data['detaylar'] = json.loads(detaylar_json)
        except:
            flash('Fatura detaylarında hata oluştu!', 'danger')
            return render_template('yeni_fatura.html', 
                                 cariler=cariler, 
                                 urunler=urunler, 
                                 birimler=birimler,
                                 today=today,
                                 fatura_no=fatura_no,
                                 form_data=fatura_data)
        
        # Validasyon
        if not fatura_data['fatura_tarihi'] or not fatura_data['cari_id']:
            flash('Fatura tarihi ve cari seçimi zorunludur!', 'danger')
            return render_template('yeni_fatura.html', 
                                 cariler=cariler, 
                                 urunler=urunler, 
                                 birimler=birimler,
                                 today=today,
                                 fatura_no=fatura_no,
                                 form_data=fatura_data)
        
        if len(fatura_data['detaylar']) == 0:
            flash('En az bir fatura kalemi eklemelisiniz!', 'danger')
            return render_template('yeni_fatura.html', 
                                 cariler=cariler, 
                                 urunler=urunler, 
                                 birimler=birimler,
                                 today=today,
                                 fatura_no=fatura_no,
                                 form_data=fatura_data)
        
        # API'ye gönder
        api_response, api_error = make_api_request('POST', '/api/fatura', fatura_data)
        
        if api_error is not None:
            flash(f'Bağlantı hatası: {api_error}', 'danger')
        elif api_response is not None:
            if api_response.status_code == 201:
                flash('Fatura başarıyla oluşturuldu!', 'success')
                return redirect(url_for('web.faturalar'))
            else:
                error_message = parse_api_error(api_response)
                flash(f'Fatura oluşturulamadı: {error_message}', 'danger')
        else:
            flash('Beklenmeyen bir hata oluştu!', 'danger')
        
        return render_template('yeni_fatura.html', 
                             cariler=cariler, 
                             urunler=urunler, 
                             birimler=birimler,
                             today=today,
                             fatura_no=fatura_no,
                             form_data=fatura_data)
    
    return render_template('yeni_fatura.html', 
                         cariler=cariler, 
                         urunler=urunler, 
                         birimler=birimler,
                         today=today,
                         fatura_no=fatura_no)


