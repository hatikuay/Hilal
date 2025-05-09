from flask import Blueprint, request, session, redirect, render_template, url_for
from app import db


insecure = Blueprint("insecure", __name__)


@insecure.route("/login", methods=["GET", "POST"])
def insecure_login():
    message = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # SELECT * FROM user WHERE username = '' OR 1=1 -- AND password = '{password}'
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(query).fetchone()

        if result:
            session["user"] = result.username if "username" in result else "admin"
            return redirect(url_for('main.dashboard'))
        else:
            # Hem main auth’la aynı metni kullanalım:
            message = "Geçersiz kullanıcı adı veya şifre."

    return render_template("insecure_login.html", message=message)

@insecure.route("/brute-login", methods=["GET", "POST"])
def brute_login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # SELECT * FROM user WHERE username = '' OR 1=1 -- AND password = '{password}'
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(query).fetchone()

        if result:
            session["user"] = result.username if "username" in result else "admin"
            return redirect(url_for('main.dashboard'))
        else:
            message = "Hatalı giriş"

    return render_template("insecure_login.html", message=message)


@insecure.route("/notes", methods=["GET", "POST"])
def insecure_notes():
    notes = []
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        notes.append({"title": title, "content": content})

    return render_template("insecure_notes.html", notes=notes)
