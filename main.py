from flask import Flask, render_template, request, Response, flash, g, redirect, session, url_for, jsonify

from flask_cors import CORS, cross_origin
import time
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
from models import Usuarios, Productos

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.route("/")
def index():
    if "logged" in session:
        return render_template("index.html")
    else:
        return redirect('login')
          

@app.before_request
def before_request():
    verificar_inactividad()

@app.after_request
def after_request(response):
    return response




# En cada solicitud (antes de procesar la solicitud)
def verificar_inactividad():
    tiempo_actual = time.time()
    tiempo_inactivo = tiempo_actual - session.get('tiempo', tiempo_actual)
    umbral_inactividad_segundos = 30
    if tiempo_inactivo > umbral_inactividad_segundos:
        session.clear() 
        session.modified = True
        form=forms.LoginForm()
        return render_template("login.html", form=form) 
    session['tiempo'] = tiempo_actual
    return None  

def password_check(passwd):

    SpecialSym =['$', '@', '#', '%']
    val = True
    mensaje = ""

    if len(passwd) < 9:
        mensaje="la contraseña debe de tener una logitud minima de 9"
        val = False

    if not any(char.isdigit() for char in passwd):
        mensaje = "La contraseña debe de tener al menos un numero"
        val = False

    if not any(char.isupper() for char in passwd):
        mensaje = "La contraseña debe de tener al menos una mayuscula"
        val = False

    if not any(char.islower() for char in passwd):
        mensaje = "La contraseña debe de tener al menos una minuscula"
        val = False

    if not any(char in SpecialSym for char in passwd):
        mensaje = "La contraseña debe de tener al menos un caracter especial '$','@','#' "
        val = False
            
    return {'valido':val,'mensaje':mensaje}



@app.route("/registro", methods = ["GET","POST"])
def registro():
    mensaje = ""
    form = forms.RegistroForm(request.form)
    print(form.nombre.data)
    if request.method == "POST" and form.validate() :
        print(form.nombre.data)
        nombre = sanitizar(form.nombre.data)
        username=form.username.data
        password=form.password.data
        username = sanitizar(username)
        password = sanitizar(password)
        
        resCheck = password_check(password)
        
        if username in password:
            mensaje = "La contraseña no debe de contener el nombre de usuario"
            return render_template("registro.html",form=form,mensaje=mensaje)
        
        if not resCheck['valido']:
            mensaje = resCheck['mensaje']
            return render_template("registro.html",form=form,mensaje=mensaje)
        
        usu=Usuarios(nombre=nombre,username=username,password=password)
        db.session.add(usu)
        db.session.commit()
        return redirect("/login")
    return render_template("registro.html",form=form,mensaje=mensaje)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm(request.form)
    res = ""
    if request.method == "POST":
        data = request.get_json()
        res = loginCompare(data["user"], data["password"])
        if res == "wronguser":
            return jsonify(fail=1)
        elif res == "wrongpass":
            return jsonify(fail=2)
        elif res == "success":
            return jsonify(success=1)
    if request.method == "GET":
        return render_template("login.html", form=form)

def loginCompare(user, password):
    user = sanitizar(user)
    password = sanitizar(password)
    emp_form = forms.LoginForm(request.form)
    usuarioEncontrado = Usuarios.query.filter_by(username=user).all()
    print(usuarioEncontrado)

    if len(usuarioEncontrado) > 0:
        if usuarioEncontrado[0].password == password:
            session["logged"] = usuarioEncontrado[0].username  # Guarda el usuario loggeado en la sesión
            session['tiempo'] = time.time()
            return "success"
        else:
            return "wrongpass"
    return "wronguser"

def sanitizar(palabra):
    palabra=str(palabra)
    if ";" in palabra or "delete" in palabra or "update" in palabra or "select" in palabra or "'" in palabra or '"' in palabra:
        palabra = palabra.replace(';', '')
        palabra = palabra.replace('delete', '')
        palabra = palabra.replace('update', '')
        palabra = palabra.replace('select', '')
        palabra = palabra.replace("'", '')
        palabra = palabra.replace('"', '')
    return palabra



@app.route("/productos", methods = ["GET","POST"])
def productos():
    productos=Productos.query.all()
    return render_template("productos.html", empleados=productos)

@app.route("/nuevoProducto", methods = ["GET","POST"])
def nuevoProducto():
    prod_form = forms.ProductoForm(request.form)
    if request.method == "POST" and prod_form.validate() :
        prod=Productos(nombre=prod_form.nombre.data, precio=prod_form.precio.data, stock=prod_form.stock.data)
        db.session.add(prod)
        db.session.commit()
        return redirect("productos")
    return render_template("nuevoProducto.html",form=prod_form)



@app.route("/eliminarProducto", methods=["GET", "POST"])
def eliminarProducto():
    form=forms.ProductoForm(request.form)
    if request.method=='GET':
        id=sanitizar(request.args.get("id"))
        name=db.session.query(Productos).filter(Productos.id==id).first().nombre
        form.id.data = id
        form.nombre.data = name
    if request.method == 'POST':
        id=sanitizar(form.id.data)
        prod=Productos.query.get(id)
        db.session.delete(prod)
        db.session.commit()
        return redirect('productos')
    return render_template("eliminar.html", form=form)


@app.route("/modificarProducto", methods=["GET", "POST"])
def modificarProducto():
    form=forms.ProductoForm(request.form)
    if request.method=='GET':
        id=sanitizar(request.args.get("id"))
        prod=db.session.query(Productos).filter(Productos.id==id).first()
        form.id.data = request.args.get("id")
        form.nombre.data=prod.nombre
        form.precio.data = prod.precio
        form.stock.data=prod.stock
    if request.method == 'POST':
        id=form.id.data
        print(id)
        print(id)
        print(id)
        prod=db.session.query(Productos).filter(Productos.id==id).first()
        print(prod.nombre)
        prod.nombre=form.nombre.data
        prod.precio=form.precio.data
        prod.stock=form.stock.data
        db.session.add(prod)
        db.session.commit()
        return redirect('productos')
    return render_template("modificar.html", form=form)



if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',debug=True)
