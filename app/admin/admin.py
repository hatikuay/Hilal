from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required
from app.models import User, Role, db
from app.forms import RegistrationForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Admin öncesi kontrol: sadece admin rolü
@admin_bp.before_request
@login_required
def restrict_admin():
    if not current_user.is_admin():
        abort(403)


# Dashboard
@admin_bp.route("/")
def dashboard():
    user_count = User.query.count()
    from app.models import Note  # Not modeli varsa

    note_count = Note.query.count() if "Note" in globals() else 0
    return render_template(
        "admin/dashboard.html", user_count=user_count, note_count=note_count
    )


# Kullanıcı listesi
@admin_bp.route("/users")
def user_list():
    users = User.query.order_by(User.id).all()
    return render_template("admin/user_list.html", users=users)


# Yeni kullanıcı oluşturma
@admin_bp.route("/create", methods=["GET", "POST"])
def create_user():
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
        db.session.commit()
        flash("Kullanıcı başarıyla oluşturuldu.", "success")
        return redirect(url_for("admin.user_list"))
    return render_template("admin/create_user.html", form=form)


# Admin yetkisi verme/geri alma
@admin_bp.route("/toggle_admin/<int:user_id>", methods=["POST"])
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Kendi yetkinizi değiştiremezsiniz.", "danger")
    else:
        user.role = Role.USER if user.role == Role.ADMIN else Role.ADMIN
        db.session.commit()
        flash("Kullanıcı rolü güncellendi.", "info")
    return redirect(url_for("admin.user_list"))


# Kullanıcı silme
@admin_bp.route("/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Kendinizi silemezsiniz.", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("Kullanıcı silindi.", "warning")
    return redirect(url_for("admin.user_list"))


# Ayarlar
@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # site adı veya diğer ayarlar kaydedilir
        flash("Ayarlar kaydedildi.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html")
