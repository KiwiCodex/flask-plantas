from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_llave_secreta'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'plantas_db'

    mysql.init_app(app)

    # Registrar el blueprint
    from .routes import main
    app.register_blueprint(main)

    return app

