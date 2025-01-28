## Requisitos
- Python 3.x
- Flask
- Flask-SQLAlchemy

## Instalación

Iniciar con la clonación:
```
git clone https://github.com/KiwiCodex/flask-plantas.git
cd flask-plantas
```
Entorno virtual:
```
python -m venv venv

#Linux
source venv/bin/activate
#Windows
venv\Scripts\activate   
```
Instalar dependencias:
```
pip install -r requirements.txt
```

Crear la base de datos (MySQL en este caso):
```
CREATE DATABASE modulos_db;
```

Configura tu base de datos en app/__init__.py:
```
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/modulos_db'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'modulos_db'

```

Inicializa la base de datos:
```
flask db init

flask db migrate -m "Inicialización de la base de datos"

flask db upgrade
```

Ejecutar aplicación:
```
python run.py
```
