from app import db

class Modulo(db.Model):
    __tablename__ = 'modulos'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False, unique=True)
    especie = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=True)

    clima_id = db.Column(db.Integer, db.ForeignKey('parametros_climaticos.id'))
    agua_id = db.Column(db.Integer, db.ForeignKey('parametros_agua.id'))
    suelo_id = db.Column(db.Integer, db.ForeignKey('parametros_suelo.id'))

    clima = db.relationship('ParametrosClimaticos', backref='modulo', lazy=True)
    agua = db.relationship('ParametrosAgua', backref='modulo', lazy=True)
    suelo = db.relationship('ParametrosSuelo', backref='modulo', lazy=True)
    especie_rango = db.relationship('EspecieRangos', backref='modulo', uselist=False)


class EspecieRangos(db.Model):
    __tablename__ = 'especie_rangos'
    id = db.Column(db.Integer, primary_key=True)
    modulo_id = db.Column(db.Integer, db.ForeignKey('modulos.id'), nullable=False)

    temperatura_min = db.Column(db.Float, nullable=False)
    temperatura_max = db.Column(db.Float, nullable=False)
    ph_min = db.Column(db.Float, nullable=False)
    ph_max = db.Column(db.Float, nullable=False)
    humedad_min = db.Column(db.Float, nullable=False)
    humedad_max = db.Column(db.Float, nullable=False)


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
