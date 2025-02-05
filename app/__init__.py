from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configuración de Flask
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "tu_llave_secreta")
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'modulos_db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/modulos_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Importar y registrar el blueprint después de inicializar Flask y SQLAlchemy
    from .routes import main
    app.register_blueprint(main)

    return app
