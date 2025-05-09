# File: app/routes.py
from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from .models import Note, User
from . import db
from .decorators import roles_required

main = Blueprint('main', __name__)


@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('user', 'admin', 'editor')
def dashboard():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_note = Note(title=title, content=content, owner=current_user)
        db.session.add(new_note)
        db.session.commit()
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', notes=notes)

from .decorators import roles_required

@main.route('/admin')
@login_required
@roles_required('admin')
def admin_panel():
    users = User.query.all()
    return render_template('admin_panel.html', users=users)