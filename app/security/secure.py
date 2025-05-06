import html
import time
from flask import Blueprint, flash, request, session, redirect, render_template, jsonify, abort, url_for
from flask_login import login_required, current_user
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import User, Note, Role
from app import db
import html

secure = Blueprint("secure", __name__)


@secure.route("/login", methods=["GET", "POST"])
def secure_login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            return redirect(url_for('secure.secure_notes'))
        else:
            flash("Giriş başarısız!")

    return render_template("secure_login.html", message=message)


failed_attempts = {}


@secure.route("/login/brute", methods=["GET", "POST"])
def secure_brute_login():

    ip = request.remote_addr
    now = time()
    cooldown = 60
    limit = 3

    if ip in failed_attempts:
        attempts, last_try = failed_attempts[ip]
        if attempts >= limit and now - last_try < cooldown:
            wait_time = int(cooldown - (now - last_try))
            return f"Çok fazla deneme! {wait_time} saniye bekleyin."

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            failed_attempts.pop(ip, None)
            return redirect(url_for('secure.secure_notes'))
        else:
            if ip not in failed_attempts:
                failed_attempts[ip] = (1, now)
            else:
                failed_attempts[ip] = (failed_attempts[ip][0] + 1, now)
            flash("Giriş başarısız!")

    return render_template("secure_brute_login.html")


@secure.route("/notes", methods=["GET", "POST"])
@login_required
def secure_notes():
    if request.method == "POST":
        # XSS korumalı
        title   = html.escape(request.form["title"])
        content = html.escape(request.form["content"])
        note = Note(title=title, content=content, owner=current_user)
        db.session.add(note)
        db.session.commit()
        flash("Not eklendi!")

    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("secure_notes.html", notes=notes)

@secure.route("/notes/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"success": True, "note_id": note_id})

@secure.route("/notes/edit/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        abort(403)
    if request.method == 'GET':
        return render_template('edit_note.html', note=note)
    if request.method == 'POST':
        # XSS korumalı güncelleme
        note.title   = html.escape(request.form["title"])
        note.content = html.escape(request.form["content"])
        db.session.commit()
        flash("Not güncellendi!")
        return redirect(url_for("secure.secure_notes"))





