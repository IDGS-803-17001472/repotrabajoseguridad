from flask import Flask, render_template, request, Response, flash, g, redirect, session, url_for
from flask_cors import CORS, cross_origin
from flask_wtf.csrf import CSRFProtect
import forms
from io import open
from google_recaptcha import ReCaptcha
app = Flask(__name__)
from config import DevelopmentConfig
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()
import secrets
cors = CORS(app, resources={r"/*": {"origins": ["*"]}})

app.config['SECRET_KEY'] = secrets.token_hex(16)
secretkey=app.config['SECRET_KEY']


from models import db
from models import Usuarios

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["GET","POST"])
def login():
    form=forms.LoginForm(request.form)
    print('Recaptcha has successded.')
    res=""
    print("dentro de login")
    if request.method == "POST" :
        data = request.get_json()
        res=loginCompare(data["user"],data["password"])
        if res=="wronguser":
            print("1")
            mensaje="El usuario no ha sido encontrado"
            flash(mensaje)
            return "baduser"
        elif res=="wrongpass":
            print("2")
            mensaje="La contraseña es incorrecta"
            flash(mensaje)
            return "badpass"
        elif res=="success":
            print("3")
            session["logged"]=True
            print(url_for('index'))
            return "3"
    if request.method == "GET" :
         return render_template("login.html", form=form) 

def loginCompare(user,password):
    user=sanitizar(user)
    password=sanitizar(password)
    emp_form=forms.LoginForm(request.form)
    usuarioEncontrado = Usuarios.query.filter_by(username=user).all()
    print(usuarioEncontrado)
    
    if len(usuarioEncontrado)>0:
        if usuarioEncontrado[0].password==password:
            return "success"
        else:
            return "wrongpass"
    return "wronguser"

def sanitizar(palabra):
    if ";" in palabra or "delete" in palabra or "update" in palabra or "select" in palabra or "'" in palabra or '"' in palabra:
        palabra = palabra.replace(';', '')
        palabra = palabra.replace('delete', '')
        palabra = palabra.replace('update', '')
        palabra = palabra.replace('select', '')
        palabra = palabra.replace("'", '')
        palabra = palabra.replace('"', '')
    return palabra


if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',debug=True)
