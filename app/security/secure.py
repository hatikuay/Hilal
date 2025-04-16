import html
import time
from flask import Blueprint, flash, request, session, redirect, render_template
from werkzeug.security import check_password_hash
from app.models import User
from app import db


secure = Blueprint("secure", __name__)


@secure.route("/insecure-login", methods=["GET", "POST"])
def secure_login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            return redirect("/dashboard")
        else:
            flash("Giriş başarısız!")

    return render_template("insecure_login.html", message=message)


failed_attempts = {}


@secure.route("/secure-brute-login", methods=["GET", "POST"])
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
            session["user"] = user.username
            failed_attempts.pop(ip, None)
            return redirect("/dashboard")
        else:
            if ip not in failed_attempts:
                failed_attempts[ip] = (1, now)
            else:
                failed_attempts[ip] = (failed_attempts[ip][0] + 1, now)
            flash("Giriş başarısız!")

    return render_template("secure_brute_login.html")


@secure.route("/secure-notes", methods=["GET", "POST"])
def insecure_notes():
    notes = []
    if request.method == "POST":
        title = html.escape(request.form["title"])
        content = html.escape(request.form["content"])

        notes.append({"title": title, "content": content})

    return render_template("insecure_notes.html", notes=notes)
