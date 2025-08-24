from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField("Повторите пароль", validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField("Создать аккаунт")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class CategoryForm(FlaskForm):
    name = StringField("Название категории", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Сохранить")


class TaskForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Описание", validators=[Optional(), Length(max=5000)])
    deadline = DateTimeLocalField("Дедлайн", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    priority = SelectField(
        "Приоритет",
        choices=[("1", "Низкий"), ("2", "Средний"), ("3", "Высокий")],
        default="2",
        validators=[DataRequired()],
    )
    category_id = SelectField("Категория", coerce=int, validators=[Optional()])

    
    is_done = BooleanField("Выполнено")
    submit = SubmitField("Сохранить")

class EmptyForm(FlaskForm):
    pass