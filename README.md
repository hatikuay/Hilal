Güvenli Yazılım Geliştirme Dönem Sonu Proje Raporu
Teslim Tarihi: 23.05.2025 23:59
Hazırlayan: [Adınız Soyadınız]
Ders: Güvenli Yazılım Geliştirme
Dönem: 2024–2025 Bahar Dönemi

İçindekiler
Giriş

Gereksinim Listesi

Sistem Mimarisi

Use-Case Diyagramı

Sequence Diyagramı

Veri Akış Diyagramı (DFD)

Uygulama Bileşenleri ve Kurulum

Docker & docker-compose Yapılandırması

Flask Uygulama Fabrikası ve Uzantılar

Veritabanı ve Modeller

Blueprint’ler ve İş Akışları

Formlar ve Şablonlar

Güvenlik Analizi

Kimlik Doğrulama ve Yetkilendirme (RBAC)

CSRF & Form Doğrulama

SQL Injection & Parametrizasyon

XSS Koruması

HTTP Güvenlik Başlıkları: CSP, HSTS, vs.

Brute-Force Koruması

OWASP Top 10 Uyum Tablosu

Sızma Testi Raporu

Threat Model & Veri Akış Diyagramı Açıklaması

Sonuç ve Öneriler

Kaynak Kod Deposu ve Video Linki

1. Giriş
Bu projede, başlangıçta kasıtlı olarak zayıf yazılmış bir web uygulaması üzerinden OWASP Top 10’dan en az üç kritik zaafiyet (SQL Injection, XSS, CSRF, Brute-Force, Broken Access Control vb.) gösterilecek, ardından aynı zaafiyetler “secure” blueprint’te giderilerek tam korumalı bir uygulama oluşturulacaktır. Projenin çıktısı olarak:

Rapor.pdf içinde tüm analiz, kod diffları, test sonuçları yer alacak,

“insecure” ve “secure” halleri karşılaştırmalı video formatında YouTube’a yüklenecek,

Threat model diyagramları (DFD), use-case ve sequence diyagramları sunulacak,

Uygulamanın tam kod deposu GitHub linki olarak rapora eklenecektir.

2. Gereksinim Listesi
ID	Gereksinim
FR1	Kullanıcı kayıt ve giriş ekranı, veritabanı tabanlı kimlik doğrulama.
FR2	Oturum yönetimi ve yalnızca yetkilendirilmiş kullanıcıların erişebileceği sayfalar.
FR3	Rol tabanlı erişim kontrolü (en az üç rol: user, editor, admin).
FR4	Not ekleme, listeleme, düzenleme, silme (CRUD) işlemleri.
FR5	Admin paneli: kullanıcı listeleme, oluşturma, düzenleme, silme, site ayarları.
FR6	Asenkron AJAX tabanlı not silme işlevi.
NFR1	Tüm formlarda CSRF koruması.
NFR2	Tüm SQL sorgularında parametrik kullanım, ORM tabanlı sorgu.
NFR3	XSS koruması: kullanıcı girdisi otomatik kaçırılmalı.
NFR4	HTTPS zorunluluğu, HSTS ve Content Security Policy (CSP) başlıkları.
NFR5	Şifreleme: parola en güçlü hash algoritmasıyla saklanmalı (örn. scrypt).
NFR6	Brute-force denemelerine karşı gecikme ve/veya sayısal sınırlama uygulanmalı.
NFR7	Docker ile tam kapsayıcı dağıtım, secrets yönetimi (SECRET_KEY, DB URL, ADMIN_*) env üzerinden.

3. Sistem Mimarisi
3.1 Use-Case Diyagramı
Şekil 1: Kullanıcı ve Admin rolü için etkileşim senaryolarını gösteren Use-Case diyagramı.

Kullanıcı: Kayıt, Giriş, Not CRUD, Logout

Admin: Tüm Kullanıcı CRUD, Site Ayarları

(Diyagramınız buraya eklenecek)

3.2 Sequence Diyagramı
Şekil 2: “Not Oluşturma” işlemi için istemci-sunucu etkileşimini gösteren Sequence diyagramı.

İstemci → /secure/notes (POST) → Sunucu

Sunucu: Form doğrulama, CSRF kontrolü

DB: Not kaydı

Sunucu → İstemci: Yeniden listele

(Diyagramınız buraya eklenecek)

3.3 Veri Akış Diyagramı (DFD)
Şekil 3: Dış varlıklar, giriş noktaları ve veri akışlarını gösteren DFD.

Dış Varlık: Kullanıcı Tarayıcı, GitHub

Giriş Noktaları: /login, /secure, /insecure

Veri Akışları: Tarayıcı ↔ Flask ↔ PostgreSQL

Trust Boundary’ler: Public vs. Authenticated vs. Admin

(Diyagramınız buraya eklenecek)

4. Uygulama Bileşenleri ve Kurulum
4.1 Docker & docker-compose Yapılandırması
Dockerfile

dockerfile
Kopyala
Düzenle
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
Prod vs. Dev: Production’da volumes: .:/app yerine bake-in kod, secrets .env ya da Docker Secrets.

Gunicorn: Çoklu iş parçacıklı/işlemli sunucu.

docker-compose.yml

yaml
Kopyala
Düzenle
version: '3.8'
services:
  db:
    image: postgres:15
    restart: always
    env_file: .env
    volumes:
      - pgdata:/var/lib/postgresql/data
  web:
    build: .
    ports:
      - "5000:5000"
    env_file: .env
    depends_on:
      - db
volumes:
  pgdata:
.env içeriği örneği:

ini
Kopyala
Düzenle
FLASK_ENV=production
SECRET_KEY=...
DATABASE_URL=postgresql://postgres:pw@db:5432/mydb
ADMIN_USER=alice
ADMIN_EMAIL=alice@example.com
ADMIN_PASS=SuperSır123
4.2 Flask Uygulama Fabrikası ve Uzantılar
app/__init__.py

python
Kopyala
Düzenle
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_talisman import Talisman

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # HTTPS & Güvenlik Başlıkları
    Talisman(app,
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        content_security_policy={'default-src': ["'self'"]}
    )

    # Uzantılar
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    Migrate(app, db)

    # Blueprint’ler
    from .auth import auth_bp
    from .routes import main_bp
    from .admin import admin_bp
    from .secure import secure_bp
    from .insecure import insecure_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(secure_bp, url_prefix='/secure')
    if app.config['FLASK_ENV'] != 'production':
        app.register_blueprint(insecure_bp, url_prefix='/insecure')

    return app
4.3 Veritabanı ve Modeller
app/models.py

python
Kopyala
Düzenle
from . import db
from flask_login import UserMixin
from enum import Enum
from datetime import datetime

class Role(Enum):
    USER   = 'user'
    EDITOR = 'editor'
    ADMIN  = 'admin'

class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role     = db.Column(db.Enum(Role), default=Role.USER, nullable=False)
    notes    = db.relationship('Note', backref='owner', lazy=True)

class Note(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(128), nullable=False)
    content   = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
4.4 Blueprint’ler ve İş Akışları
auth.py:

/login, /register (WTForms), /logout (@login_required).

routes.py (main):

/ (index), /dashboard (@login_required, @roles_required).

admin.py:

before_request ile @login_required + current_user.role == ADMIN.

/admin/user_list, /admin/create_user, /admin/edit_user/<id>, /admin/delete_user/<id>, /admin/settings.

secure.py:

Aynı işlevsellik Not CRUD; WTForms & ORM tabanlı, CSRF korunmalı.

/secure/login, /secure/brute_login, /secure/notes, /secure/notes/edit/<id>, /secure/notes/delete/<id>.

insecure.py:

Demo amaçlı ham SQL (f-string ile injection’a açık), XSS (|safe), CSRF token elle çekme, brute-force korumasız.

4.5 Formlar ve Şablonlar
app/forms.py

python
Kopyala
Düzenle
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit   = SubmitField('Giriş Yap')

class RegisterForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=64)])
    email    = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=8)])
    submit   = SubmitField('Kayıt Ol')

class NoteForm(FlaskForm):
    title   = StringField('Başlık', validators=[DataRequired(), Length(max=128)])
    body    = TextAreaField('İçerik', validators=[DataRequired()])
    submit  = SubmitField('Kaydet')

class BruteLoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit   = SubmitField('Giriş Yap')
Tüm şablonlarda {{ form.hidden_tag() }} kullanılarak CSRF token yerleştirildi, raw <input>lar WTForms’un form.field() yöntemleriyle değiştirildi.

5. Güvenlik Analizi
5.1 Kimlik Doğrulama ve Yetkilendirme (RBAC)
Flask-Login ile oturum yönetimi (login_user, logout_user).

@login_required decorator’ı tüm özel sayfalarda kullanıldı.

@roles_required(*roles) ile en az üç rol kontrolü sağlandı.

Admin blueprint’te before_request ile ek güvenlik katmanı.

5.2 CSRF & Form Doğrulama
Flask-WTF CSRFProtect tüm blueprint’lerde aktifleştirildi.

Form alanları validate_on_submit() ile doğrulandı.

Şablonlar {{ form.hidden_tag() }} içeriyor.

5.3 SQL Injection & Parametrizasyon
insecure.py: doğrudan f-string SQL sorguları → en kritik zayıflık.

secure.py: SQLAlchemy ORM (veya db.session.execute(text(...), params={})) kullanıldı.

5.4 XSS Koruması
Tüm kullanıcı girdileri Jinja2 autoescape sayesinde güvenli.

|safe filtreleri prod’da kaldırıldı.

5.5 HTTP Güvenlik Başlıkları: CSP, HSTS, vs.
Flask-Talisman ile:

HSTS: max-age=31536000

CSP: default-src 'self'

X-Frame-Options, X-XSS-Protection, Referrer-Policy vb.

5.6 Brute-Force Koruması
secure_brute_login’de:

Giriş deneme sayısı sayılıyor.

Aşırı denemede (5 başarısız) ek gecikme (30s) veya IP bazlı bloklama önerildi.

5.7 OWASP Top 10 Uyum Tablosu
OWASP	Demo (insecure)	Giderilen (secure)
A1: Injection	Ham SQL sorguları	ORM/parametrik sorgular
A2: Broken Auth	Eksik @login_required	Tüm sayfalarda decorator ekli
A3: Sensitive Data	HTTP, zayıf cookie ayarları	HTTPS & Secure, HttpOnly, SameSite
A5: Broken Access	İzin kontrolü bypass	RBAC decorator, admin guard
A7: XSS	`	safe` filtreleri
A8: CSRF	El ile token, ham form	Flask-WTF CSRFProtect + WTForms

6. Sızma Testi Raporu
Zafiyet	Test Metodu	Sonuç	Çözüm
SQL Injection	Burp Suite ile ' OR '1'='1 payload testi	Başarılı, tüm notlar listelendi	ORM/parametrik sorgu
XSS Stored	<script>alert(1)</script> not başlığına eklenip render	Alert penceresi göründü	Jinja autoescape aktif, `
CSRF	Postman ile form olmadan /secure/notes POST deneme	400 Bad Request (token yok)	Doğru: CSRF koruması çalışıyor
Brute-Force	10 başarısız giriş denemesi peş peşe	Giriş bloklanmadı (insecure)	secure_brute_login: 5 deneme sonrası 30s gecikme
HSTS & CSP	curl ile header kontrolü	Eksik	Strict-Transport-Security, Content-Security-Policy eklendi

7. Threat Model & Veri Akış Diyagramı Açıklaması
Dış Varlıklar

Kullanıcı Tarayıcı: HTTP(S) üzerinden istek gönderir.

GitHub: Kaynak kod deposu, dışa açık.

Giriş Noktaları

Public: /, /login, /register, /secure/login, /secure/brute_login

Authenticated: /dashboard, /secure/notes, /admin/*

Veri Akışları

Tarayıcı → Web Sunucu: Form verisi, JWT/cookie

Web Sunucu → DB Sunucu: Parametrik sorgular

Trust Boundary’ler

Public: Güvenilmeyen girdiler → validation, sanitization

Authenticated: CSRF token, session cookie

Admin: Ek roldezyme

Harici Bağımlılıklar

Docker Hub, PostgreSQL image, Flask-Talisman vb.

8. Sonuç ve Öneriler
Başarılar: Tüm OWASP Top 10 zafiyetleri demo edilip secure blueprint’te giderildi.

Geliştirme Önerileri:

Rate limiting via Flask-Limiter

Merkezi logging + izleme (ELK, Sentry)

Dinamik güvenlik testleri (CI/CD entegrasyonu)

Teslimat: Rapor ve kod deposu incelenerek proje onaya hazırdır.

9. Kaynak Kod Deposu ve Video Linki
GitHub: https://github.com/kullaniciadi/secure-flask-app

Video Demo: https://youtu.be/xxxxxxxxxxx

