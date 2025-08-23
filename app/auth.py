from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from .forms import RegisterForm, LoginForm
from .models import User
from . import db


auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.tasks"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует", "danger")
            return render_template("auth/register.html", form=form)
        user = User(email=email)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Не удалось создать аккаунт. Попробуйте другой email.", "danger")
            return render_template("auth/register.html", form=form)
        login_user(user)
        flash("Аккаунт создан!", "success")
        return redirect(url_for("main.tasks"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.tasks"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Добро пожаловать!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.tasks"))
        flash("Неверный email или пароль", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Вы вышли из аккаунта", "info")
    return redirect(url_for("auth.login"))