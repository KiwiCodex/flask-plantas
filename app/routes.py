from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Modulo, EspecieRangos
from app import db

# Define el blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    modulos = Modulo.query.all()  # Obtener todos los módulos
    return render_template('index.html', modulos=modulos)

@main.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Obtener datos del formulario
        numero = request.form['numero']
        especie = request.form['especie']
        temperatura_min = request.form['temperatura_min']
        temperatura_max = request.form['temperatura_max']
        ph_min = request.form['ph_min']
        ph_max = request.form['ph_max']
        humedad_min = request.form['humedad_min']
        humedad_max = request.form['humedad_max']

        # Crear las instancias de Modulo y EspecieRangos
        nuevo_modulo = Modulo(numero=numero, especie=especie)
        db.session.add(nuevo_modulo)
        db.session.commit()  # Guardar para obtener el ID del módulo

        nuevos_rangos = EspecieRangos(
            modulo_id=nuevo_modulo.id,
            temperatura_min=temperatura_min,
            temperatura_max=temperatura_max,
            ph_min=ph_min,
            ph_max=ph_max,
            humedad_min=humedad_min,
            humedad_max=humedad_max
        )
        db.session.add(nuevos_rangos)
        db.session.commit()

        flash("Módulo agregado exitosamente.")
        return redirect(url_for('main.index'))

    return render_template('create.html')

@main.route('/modulos/<int:id>')
def show(id):
    modulo = Modulo.query.get_or_404(id)  # Obtener el módulo por su ID
    return render_template('show.html', modulo=modulo, rangos=modulo.especie_rango)

@main.route('/simulate/<int:id>')
def simulate(id):
    modulo = Modulo.query.get_or_404(id)
    rangos = modulo.especie_rango

    if not rangos:
        flash("No se encontraron rangos para este módulo.")
        return redirect(url_for('main.index'))

    # Generar valores simulados
    import random
    valores_simulados = {
        'temperatura': random.uniform(10, 40),
        'ph': random.uniform(4, 9),
        'humedad': random.randint(10, 100)
    }

    # Determinar si están dentro del rango ideal
    condiciones = {
        'temperatura': rangos.temperatura_min <= valores_simulados['temperatura'] <= rangos.temperatura_max,
        'ph': rangos.ph_min <= valores_simulados['ph'] <= rangos.ph_max,
        'humedad': rangos.humedad_min <= valores_simulados['humedad'] <= rangos.humedad_max
    }

    # Determinar estado general (verde, amarillo, naranja, rojo)
    estado_color = 'green'
    if not all(condiciones.values()):
        estado_color = 'yellow' if sum(condiciones.values()) == 2 else 'orange' if sum(condiciones.values()) == 1 else 'red'

    return render_template(
        'simulate.html',
        modulo=modulo,
        valores_simulados=valores_simulados,
        condiciones=condiciones,
        estado_color=estado_color
    )

@main.route('/modulos/<int:id>/delete', methods=['POST'])
def delete(id):
    modulo = Modulo.query.get_or_404(id)
    if modulo.especie_rango:
        db.session.delete(modulo.especie_rango)
    db.session.delete(modulo)
    db.session.commit()

    flash("Módulo eliminado exitosamente.")
    return redirect(url_for('main.index'))
