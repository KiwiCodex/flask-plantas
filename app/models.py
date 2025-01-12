from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Planta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    temperatura_min = db.Column(db.Float, nullable=False)
    temperatura_max = db.Column(db.Float, nullable=False)
    ph_min = db.Column(db.Float, nullable=False)
    ph_max = db.Column(db.Float, nullable=False)
    humedad_min = db.Column(db.Float, nullable=False)
    humedad_max = db.Column(db.Float, nullable=False)
