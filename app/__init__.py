# File: app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
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

    return app
