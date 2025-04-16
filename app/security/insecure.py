from flask import Blueprint, request, session, redirect, render_template
from app import db


insecure = Blueprint("insecure", __name__)


@insecure.route("/insecure-login", methods=["GET", "POST"])
def insecure_login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        #SELECT * FROM user WHERE username = '' OR 1=1 -- AND password = '{password}'
        query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(query).fetchone()

        if result:
            session["user"] = result.username if "username" in result else "admin"
            return redirect("/dashboard")
        else:
            message = "Hatalı giriş"

    return render_template("insecure_login.html", message=message)

@insecure.route("/insecure-notes", methods=["GET", "POST"])
def insecure_notes():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        #SELECT * FROM user WHERE username = '' OR 1=1 -- AND password = '{password}'
        query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(query).fetchone()

        if result:
            session["user"] = result.username if "username" in result else "admin"
            return redirect("/dashboard")
        else:
            message = "Hatalı giriş"

    return render_template("insecure_login.html", message=message)


