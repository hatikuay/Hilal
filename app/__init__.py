# File: app/__init__.py

from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Lütfen önce giriş yapın."
login_manager.login_message_category = "warning"
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    Migrate(app, db)
    

    # --- Unauthorized (not logged-in) handler ---
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        # Oturum açmamış kullanıcıları login sayfasına yönlendir, next param ile geri dönüş imkânı ver
        return redirect(url_for('auth.login', next=request.path))
    
    # --- Forbidden (403) handler ---
    @app.errorhandler(403)
    def forbidden(error):
        # Abort(403) çağrıldığında gösterilecek sayfa
        return render_template('403.html'), 403

    
    # --- Context processor: tüm şablonlarda Role enum’u erişilebilir kıl ---
    @app.context_processor
    def inject_role_enum():
        from app.models import Role
        return dict(Role=Role)

    # --- Blueprints ---
    from app.auth import auth as auth_bp
    from app.routes import main as main_bp
    from app.security.insecure import insecure as insecure_bp
    from app.security.secure import secure as secure_bp
    from app.admin.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(insecure_bp, url_prefix='/insecure')
    app.register_blueprint(secure_bp, url_prefix='/secure')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app
