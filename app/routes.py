from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import mysql

# Define el blueprint
main = Blueprint('main', __name__)

from MySQLdb.cursors import DictCursor  # Importar DictCursor

def get_plantas():
    cur = mysql.connection.cursor(DictCursor)  # Usar DictCursor
    cur.execute("SELECT id, nombre FROM plantas")
    plantas = cur.fetchall()
    return plantas


@main.route('/')
def index():
    plantas = get_plantas()
    return render_template('index.html', plantas=plantas)

@main.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        temperatura_min = request.form['temperatura_min']
        temperatura_max = request.form['temperatura_max']
        ph_min = request.form['ph_min']
        ph_max = request.form['ph_max']
        humedad_min = request.form['humedad_min']
        humedad_max = request.form['humedad_max']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO plantas (nombre, temperatura_min, temperatura_max, ph_min, ph_max, humedad_min, humedad_max) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nombre, temperatura_min, temperatura_max, ph_min, ph_max, humedad_min, humedad_max)
        )
        mysql.connection.commit()
        flash("Planta agregada exitosamente.")
        return redirect(url_for('main.index'))

    return render_template('create.html')

@main.route('/plantas/<int:id>')
def show(id):
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM plantas WHERE id = %s", (id,))
    planta = cur.fetchone()  # Esto debe devolver un diccionario
    return render_template('show.html', planta=planta)

import random

@main.route('/simulate/<int:id>')
def simulate(id):
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM plantas WHERE id = %s", (id,))
    planta = cur.fetchone()
    
    if not planta:
        return "Planta no encontrada", 404

    # Generar valores simulados
    valores_simulados = {
        'temperatura': random.uniform(10, 40),
        'ph': random.uniform(4, 9),
        'humedad': random.randint(10, 100)
    }

    # Determinar si están dentro del rango ideal
    rangos = {
        'temperatura': planta['temperatura_min'] <= valores_simulados['temperatura'] <= planta['temperatura_max'],
        'ph': planta['ph_min'] <= valores_simulados['ph'] <= planta['ph_max'],
        'humedad': planta['humedad_min'] <= valores_simulados['humedad'] <= planta['humedad_max']
    }

    # Determinar estado general (verde, amarillo, naranja, rojo)
    estado_color = 'green'
    if not all(rangos.values()):
        estado_color = 'yellow' if sum(rangos.values()) == 2 else 'orange' if sum(rangos.values()) == 1 else 'red'

    return render_template(
        'simulate.html',
        planta=planta,
        valores_simulados=valores_simulados,
        rangos=rangos,
        estado_color=estado_color
    )


@main.route('/plantas/<int:id>/delete', methods=['POST'])
def delete(id):
    # Conectar a la base de datos
    cur = mysql.connection.cursor()
    
    # Eliminar la planta por su ID
    cur.execute("DELETE FROM plantas WHERE id = %s", (id,))
    mysql.connection.commit()
    
    # Confirmación al usuario
    flash("Planta eliminada exitosamente.")
    
    # Redirigir a la lista principal de plantas
    return redirect(url_for('main.index'))

