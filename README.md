## Requisitos
- Python 3.x
- Flask
- Flask-SQLAlchemy

## Instalación

Iniciar con la clonación:
```
git clone https://github.com/KiwiCodex/flask-plantas.git
```
Entorno virtual:
```
python -m venv venv

source venv/bin/activate  //Linux
venv\Scripts\activate   //Windows
```
Instalar dependencias:
```
pip install -r requirements.txt
```

Configura tu base de datos en app/__init__.py:
```
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/modulos_db'
```

Inicializa la base de datos:
```
flask db upgrade
flask run
```

