# File: app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from config import Config
from flask_migrate import Migrate
from flask import render_template

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    
    # 1) Login yönlendirme ve mesajları
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen önce giriş yapın.'
    login_manager.login_message_category = 'warning'

    # 2) Yetkisiz erişim (401 yerine 403) için özel handler
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        # Giriş yapılmamışsa önce login sayfasına yönlendirir,
        # ancak roles_required ile abort(403) sonrası burası çalışacak.
        return render_template('403.html'), 403
    
    csrf.init_app(app)
    
    # Context processor: tüm şablonlarda Role isimle erişilebilir kıl
    @app.context_processor
    def inject_role_enum():
        from app.models import Role
        return dict(Role=Role)

    # Blueprints
    from app.auth import auth as auth_bp
    from app.routes import main as main_bp
    from app.security.insecure import insecure as insecure_bp
    from app.security.secure import secure as secure_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(insecure_bp, url_prefix='/insecure')
    app.register_blueprint(secure_bp, url_prefix='/secure')
    
    migrate = Migrate(app, db)
    return app
