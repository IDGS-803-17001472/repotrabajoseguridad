from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, PasswordField
from wtforms import validators
from flask_wtf.recaptcha import RecaptchaField

class LoginForm(Form):
    usuario = StringField('usuario', [
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=20, message='ingresa un usuario valido')
    ])
    password = PasswordField('contraseña',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=20, message='ingresa una contraseña valida')
    ])
    recaptcha = RecaptchaField()


