# File: app/auth.py
from flask import Blueprint, render_template, redirect, request, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User, Role
from . import db, login_manager
from .forms import LoginForm, RegistrationForm
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 1) Kullanıcıyı bul
        user = User.query.filter_by(username=form.username.data).first()
        # 2) Şifreyi doğrula
        if user and check_password_hash(user.password, form.password.data):
            # 3) Oturumu aç ve "remember" opsiyonunu geçir
            login_user(user, remember=form.remember.data)
            flash('Başarıyla giriş yaptınız.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        # Hatalı kullanıcı/şifre — artık tek, generic mesaj
        flash('Geçersiz kullanıcı adı veya şifre.', 'danger')
    # GET isteği veya form validasyon hataları
    return render_template('login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(
                form.password.data, method='scrypt'),
            role=form.role.data
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Kayıt başarıyla tamamlandı. Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash(
                'Bu e-posta zaten kullanımda. Lütfen başka bir e-posta deneyin.', 'danger')
    return render_template('register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login'))
