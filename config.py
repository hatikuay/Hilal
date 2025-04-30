import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@db:5432/mydatabase"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # === Güvenli Çerez Ayarları ===
    SESSION_COOKIE_SECURE = True # Sadece HTTPS üzerinde gönderilsin
    SESSION_COOKIE_HTTPONLY = True # JavaScript’in document.cookie ile erişimi engelle
    SESSION_COOKIE_SAMESITE = "Lax" # CSRF riskini azaltmak için
    
    SESSION_COOKIE_SECURE   = os.environ.get("FLASK_ENV") == "production"
    REMEMBER_COOKIE_SECURE  = os.environ.get("FLASK_ENV") == "production" 
    REMEMBER_COOKIE_SAMESITE = "Lax"
    
    # === Oturum Süresi ===
    # session.permanent=True yapıldığında geçerli olacak maksimum süre
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

