from flask_sqlalchemy import SQLAlchemy

import datetime

db=SQLAlchemy()

class Usuarios(db.Model):
    _tablename_='usuarios'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(50))
    username=db.Column(db.String(50))
    password=db.Column(db.String(50))
    
class Productos(db.Model):
    _tablename_='productos'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(50))
    precio=db.Column(db.Double)
    stock=db.Column(db.Integer)

