from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user
from .models import User, Note, Role
from . import db

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return redirect("/login")


@main.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        new_note = Note(title=title, content=content, owner=current_user)
        db.session.add(new_note)
        db.session.commit()

    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", notes=notes)


@main.route("/admin")
@login_required
def admin_panel():

    if current_user.role != Role.ADMIN:
        flash("Yetkisiz erişim!")
        return redirect("/dashboard")

    users = User.query.all()
    return render_template("admin_panel.html", users=users)
