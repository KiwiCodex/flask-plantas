from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_migrate import Migrate

mysql = MySQL()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_llave_secreta'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'modulos_db'

    # Configuración de SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/modulos_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    mysql.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Importar modelos para que sean registrados
    from app.models import Modulo, EspecieRangos, ParametrosClimaticos, ParametrosAgua, ParametrosSuelo

    # Registrar el blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
