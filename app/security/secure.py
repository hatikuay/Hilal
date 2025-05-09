# File: app/security/secure.py

import html
from time import time
from flask import (
    Blueprint,
    flash,
    request,
    session,
    redirect,
    render_template,
    jsonify,
    abort,
    url_for,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from app.models import User, Note
from app import db

secure = Blueprint("secure", __name__)


@secure.route("/login", methods=["GET", "POST"])
def secure_login():
    """
    Normal login: username/password kontrolü + 'next' parametresiyle geri dönüş
    """
    # Eğer zaten login olmuşsa doğrudan notlar sayfasına
    if current_user.is_authenticated:
        return redirect(url_for('secure.secure_notes'))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            # next parametreyle geldi mi?
            next_page = request.args.get("next")
            return redirect(next_page or url_for('secure.secure_notes'))
        else:
            flash("Geçersiz kullanıcı adı veya şifre.", "danger")

    return render_template("secure_login.html")

failed_attempts = {}

@secure.route("/login/brute", methods=["GET", "POST"])
def secure_brute_login():
    """
    Basit IP tabanlı brute-force koruması:
    max 3 deneme, ardından 60 sn cool-down
    """
    ip = request.remote_addr
    now = time()
    cooldown = 60  # saniye
    limit = 3

    # Cool-down uygulaması
    if ip in failed_attempts:
        attempts, last_try = failed_attempts[ip]
        if attempts >= limit and (now - last_try) < cooldown:
            wait_time = int(cooldown - (now - last_try))
            flash(f"Çok fazla deneme! Lütfen {wait_time} sn sonra tekrar deneyin.", "warning")
            return render_template("secure_brute_login.html")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            failed_attempts.pop(ip, None)
            return redirect(url_for('secure.secure_notes'))
        else:
            # Başarısız deneme kaydı
            if ip not in failed_attempts:
                failed_attempts[ip] = (1, now)
            else:
                failed_attempts[ip] = (failed_attempts[ip][0] + 1, now)
            flash("Geçersiz kullanıcı adı veya şifre.", "danger")

    return render_template("secure_brute_login.html")


@secure.route("/notes", methods=["GET", "POST"])
@login_required
def secure_notes():
    """
    Notları listele / yeni not ekle
    """
    if request.method == "POST":
        title = html.escape(request.form.get("title", ""))
        content = html.escape(request.form.get("content", ""))
        note = Note(title=title, content=content, owner=current_user)
        db.session.add(note)
        db.session.commit()
        flash("Not eklendi!", "success")

    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("secure_notes.html", notes=notes)


@secure.route("/notes/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    """
    AJAX ile silme: {success: True, note_id}
    """
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"success": True, "note_id": note_id})


@secure.route("/notes/edit/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    """
    Not düzenleme formu ve kayıt işlemi
    """
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        abort(403)

    if request.method == 'GET':
        return render_template('edit_note.html', note=note)

    # POST: güncelleme
    note.title   = html.escape(request.form.get("title", ""))
    note.content = html.escape(request.form.get("content", ""))
    db.session.commit()
    flash("Not güncellendi!", "success")
    return redirect(url_for("secure.secure_notes"))
