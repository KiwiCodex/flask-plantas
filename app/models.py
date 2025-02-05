from app import db
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

class Escuela(db.Model):
    __tablename__ = 'escuelas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    comuna = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(255), nullable=True)
    profesor = db.Column(db.String(255), nullable=True)
    curso = db.Column(db.String(255), nullable=True)
    coordenadas = db.Column(Geometry('POINT'))

    modulos = db.relationship('ModuloEscolar', backref='escuela', lazy=True)

class ModuloEscolar(db.Model):
    __tablename__ = 'modulos_escolares'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=True)
    coordenadas = db.Column(Geometry('POINT'))
    
    id_dataloger = db.Column(db.Integer, db.ForeignKey('datalogers.id'))
    id_planta = db.Column(db.Integer, db.ForeignKey('plantas.id'))
    id_escuela = db.Column(db.Integer, db.ForeignKey('escuelas.id'))
    
    dataloger = db.relationship('Dataloger', backref='modulo', lazy=True)
    planta = db.relationship('Planta', backref='modulo', lazy=True)

class Dataloger(db.Model):
    __tablename__ = 'datalogers'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    api_token = db.Column(db.String(255), nullable=False)
    api_url = db.Column(db.String(255), nullable=False)

class Planta(db.Model):
    __tablename__ = 'plantas'
    id = db.Column(db.Integer, primary_key=True)
    especie = db.Column(db.String(255), nullable=False)
    fecha_plantado = db.Column(db.Date, nullable=True)
    fecha_cosecha = db.Column(db.Date, nullable=True)

    rangos = db.relationship('Rangos', backref='planta', lazy=True)

class Variables(db.Model):
    __tablename__ = 'variables'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    unidad_medida = db.Column(db.String(50), nullable=False)

class Rangos(db.Model):
    __tablename__ = 'rangos'
    id = db.Column(db.Integer, primary_key=True)
    temperatura_min = db.Column(db.Float, nullable=False)
    temperatura_max = db.Column(db.Float, nullable=False)
    ph_min = db.Column(db.Float, nullable=False)
    ph_max = db.Column(db.Float, nullable=False)
    humedad_min = db.Column(db.Float, nullable=False)
    humedad_max = db.Column(db.Float, nullable=False)
    
    id_planta = db.Column(db.Integer, db.ForeignKey('plantas.id'))
    id_variable = db.Column(db.Integer, db.ForeignKey('variables.id'))

class MedicionesBajadas(db.Model):
    __tablename__ = 'mediciones_bajadas'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=func.now())
    valor = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=True)
    
    id_dataloger = db.Column(db.Integer, db.ForeignKey('datalogers.id'))
    id_planta = db.Column(db.Integer, db.ForeignKey('plantas.id'))


'''
class ParametrosClimaticos(db.Model):
    __tablename__ = 'parametros_climaticos'
    id = db.Column(db.Integer, primary_key=True)
    temperatura = db.Column(db.Float, nullable=False)
    humedad = db.Column(db.Float, nullable=False)
    precipitaciones = db.Column(db.Float, nullable=False)
    radiacion_global = db.Column(db.Float, nullable=False)
    radiacion_uv = db.Column(db.Float, nullable=False)


class ParametrosAgua(db.Model):
    __tablename__ = 'parametros_agua'
    id = db.Column(db.Integer, primary_key=True)
    ph = db.Column(db.Float, nullable=False)
    salinidad = db.Column(db.Float, nullable=False)
    cloruro = db.Column(db.Float, nullable=False)
    boro = db.Column(db.Float, nullable=False)


class ParametrosSuelo(db.Model):
    __tablename__ = 'parametros_suelo'
    id = db.Column(db.Integer, primary_key=True)
    humedad = db.Column(db.Float, nullable=False)
    potencial_matrico = db.Column(db.Float, nullable=False)
    temperatura = db.Column(db.Float, nullable=False)
    salinidad = db.Column(db.Float, nullable=False)


//Para relacionarlos después en otra entidad//:
clima = db.relationship('ParametrosClimaticos', backref='modulo', lazy=True)
agua = db.relationship('ParametrosAgua', backref='modulo', lazy=True)
suelo = db.relationship('ParametrosSuelo', backref='modulo', lazy=True)
especie_rango = db.relationship('EspecieRangos', backref='modulo', uselist=False)

'''