
Pasos para utilizar la aplicación y realizar migraciones:
```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Configura tu base de datos en app/__init__.py:
```
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:contraseña@localhost/nombre_base_datos'
```

Inicializa la base de datos:
```
flask db upgrade
flask run
```

