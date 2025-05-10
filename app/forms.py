# File: app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from .models import User, Role


class LoginForm(FlaskForm):
    username = StringField(
        "Kullanıcı Adı",
        validators=[
            DataRequired(message="Kullanıcı adı boş olamaz"),
            Length(min=3, max=150),
        ],
    )
    password = PasswordField(
        "Şifre", validators=[DataRequired(message="Şifre boş olamaz")]
    )
    remember = BooleanField("Beni Hatırla")
    submit = SubmitField("Giriş Yap")


class RegistrationForm(FlaskForm):
    username = StringField(
        "E-posta",
        validators=[DataRequired("E-posta boş olamaz"), Length(min=6, max=150)],
    )
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField(
        "Şifre", validators=[DataRequired("Şifre boş olamaz"), Length(min=6)]
    )
    confirm = PasswordField(
        "Şifre (Tekrar)",
        validators=[
            DataRequired("Şifre tekrar boş olamaz"),
            EqualTo("password", message="Şifreler uyuşmuyor"),
        ],
    )
    # --- Buraya rol seçimi ekliyoruz ---
    role = SelectField(
        "Rol",
        choices=[
            (Role.GUEST, "Guest"),
            (Role.USER, "User"),
            (Role.EDITOR, "Editor"),
            # Admini normal kayıt yoluyla açığa çıkarmak istemiyorsanız buraya eklemeyin
        ],
        default=Role.USER,
        validators=[DataRequired()],
    )
    submit = SubmitField("Kayıt Ol")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Bu e-posta zaten kayıtlı.")

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 128)])
    body = TextAreaField('Content', validators=[DataRequired(), Length(1, 1024)])
    submit = SubmitField('Submit')
