from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


# Форма регистрации
class RegistrationForm(FlaskForm):
    username = StringField('Никнейм', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    active = BooleanField('Активный', default=True)
    submit = SubmitField('Зарегистрироваться')

    # Добавляем скрытое поле CSRF-токена
    csrf_token = StringField()


# Форма входа
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


# Форма редактирования данных пользователя
class EditProfileForm(FlaskForm):
    username = StringField('Никнейм', validators=[DataRequired()])
    submit = SubmitField('Тык')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username


# Форма выполнения Тренировки Дня. Галочка.
class ResultForm(FlaskForm):
    result = BooleanField('Результат, True или Не True?', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
