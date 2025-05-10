import html
from functools import wraps
from flask import (
    Blueprint, request, session,
    redirect, render_template, url_for, flash
)
from app import db

insecure = Blueprint("insecure", __name__)

# Basit oturum kontrol decoator'u
def require_session_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for('insecure.insecure_login'))
        return f(*args, **kwargs)
    return decorated

# Normal login (SQL inj. açık)
@insecure.route("/login", methods=["GET", "POST"])
def insecure_login():
    if session.get("user"):
        return redirect(url_for('insecure.insecure_notes'))

    message = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(query).fetchone()

        if result:
            session["user"] = getattr(result, "username", username)
            return redirect(url_for('insecure.insecure_notes'))
        else:
            message = "Geçersiz kullanıcı adı veya şifre."

    return render_template("insecure_login.html", message=message)

# Brute-force demo login (aynı mesaj)
failed_attempts = {}
@insecure.route("/brute-login", methods=["GET", "POST"])
def brute_login():
    if session.get("user"):
        return redirect(url_for('insecure.insecure_notes'))

    message = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(query).fetchone()

        if result:
            session["user"] = getattr(result, "username", username)
            return redirect(url_for('insecure.insecure_notes'))
        else:
            message = "Geçersiz kullanıcı adı veya şifre."

    return render_template("insecure_brute_login.html", message=message)

# Güvenlik kontrolü eklenmiş notlar sayfası
@insecure.route("/notes", methods=["GET", "POST"])
@require_session_login
def insecure_notes():
    notes = session.setdefault("notes", [])
    if request.method == "POST":
        title = request.form.get("title", "")
        content = request.form.get("content", "")
        notes.append({"title": title, "content": content})
        session["notes"] = notes
    return render_template("insecure_notes.html", notes=notes)

# Logout route\@insecure.route("/logout")
def insecure_logout():
    session.pop("user", None)
    return redirect(url_for('insecure.insecure_login'))
