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
CREATE DATABASE "huertos_db";
```

Configura tu base de datos en app/__init__.py:
```
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/huertos_db'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'huertos_db'

```

Inicializa la base de datos:
```
flask db init

flask db migrate -m "Inicialización de la base de datos"
```
Antes de migrar la base de datos debe colocar esta librería en su archivo de actualización (migrations/versions/"nombreArchivo".py):
```
import geoalchemy2
```
Ahora se aplica:
```
flask db upgrade
```


Ejecutar aplicación:
```
python run.py
```

Para la API_KEY, se debe crear un archivo .env:
```
API_TOKEN="Tu_API_KEY"
```




