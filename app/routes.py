from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import ModuloEscolar, Planta, Rangos, Escuela
from app import db
from colegios import COLEGIOS
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from .api_client import obtener_datos


# Define el blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    modulos = ModuloEscolar.query.all()  # Obtener todos los módulos
    return render_template('index.html', modulos=modulos)

@main.route('/escuelas')
def escuela_lista():
    escuelas = Escuela.query.all()  # Obtener todas las escuelas de la BD
    return render_template('escuela_lista.html', escuelas=escuelas)

@main.route('/escuela/crear', methods=['GET', 'POST'])
def escuela_crear():
    if request.method == 'POST':
        try:
            data = request.form  # Datos desde el formulario HTML

            nombre = data.get("nombre")
            coordenadas_wkt = COLEGIOS.get(nombre)
            comuna = data.get("comuna")
            director = data.get("director")
            profesor = data.get("profesor")
            curso = data.get("curso")

            if not coordenadas_wkt:
                flash("Colegio no válido", "danger")
                return redirect(url_for('main.escuela_crear'))

            # Convertir WKT a objeto POINT
            lon, lat = coordenadas_wkt.replace("POINT (", "").replace(")", "").strip().split()
            lon = round(float(lon.strip().rstrip(',')), 6)
            lat = round(float(lat.strip().rstrip(',')), 6)
            point_geom = from_shape(Point(lon, lat))

            # Verificar si ya existe una escuela con los mismos datos excepto el curso
            escuela_existente = Escuela.query.filter_by(
                nombre=nombre,
                coordenadas=point_geom,
                comuna=comuna,
                director=director,
                profesor=profesor
            ).first()

            if escuela_existente and escuela_existente.curso == curso:
                flash("Ya existe una escuela con los mismos datos y curso. Cambie al menos un campo.", "danger")
                return redirect(url_for('main.escuela_crear'))

            # Crear la nueva escuela
            nueva_escuela = Escuela(
                nombre=nombre,
                coordenadas=point_geom,
                comuna=comuna,
                director=director,
                profesor=profesor,
                curso=curso
            )

            db.session.add(nueva_escuela)
            db.session.commit()

            flash("Escuela creada correctamente", "success")
            return redirect(url_for('main.escuela_lista'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('main.escuela_crear'))

    return render_template('escuela_crear.html', COLEGIOS=COLEGIOS)

@main.route('/escuela/editar/<int:id>', methods=['GET', 'POST'])
def escuela_editar(id):
    escuela = Escuela.query.get_or_404(id)

    if request.method == 'POST':
        escuela.nombre = request.form['nombre']
        escuela.comuna = request.form['comuna']
        escuela.director = request.form['director']
        escuela.profesor = request.form['profesor']
        escuela.curso = request.form['curso']

        db.session.commit()
        flash("Escuela actualizada correctamente", "success")
        return redirect(url_for('main.escuela_lista'))

    return render_template('escuela_editar.html', escuela=escuela)


@main.route('/escuela/eliminar/<int:id>', methods=['POST'])
def escuela_eliminar(id):
    escuela = Escuela.query.get_or_404(id)
    db.session.delete(escuela)
    db.session.commit()
    flash("Escuela eliminada correctamente", "success")
    return redirect(url_for('main.escuela_lista'))

@main.route('/api/datos')
def api_datos():
    """Devuelve datos desde la API de ZentraCloud."""
    start_date = request.args.get("start_date", "2025-01-01 00:00:00")
    end_date = request.args.get("end_date", "2025-02-02 00:00:00")

    datos_nube = obtener_datos(start_date, end_date)
    if datos_nube is None:
        return jsonify({"error": "No se pudieron obtener los datos"}), 500

    return jsonify(datos_nube)



'''
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

        # Crear instancia de ModuloEscolar
        nuevo_modulo = ModuloEscolar(nombre=numero)
        db.session.add(nuevo_modulo)
        db.session.commit()  # Guardar para obtener el ID del módulo

        # Crear una nueva planta asociada al módulo
        nueva_planta = Planta(especie=especie)
        db.session.add(nueva_planta)
        db.session.commit()

        # Asociar la planta al módulo
        nuevo_modulo.id_planta = nueva_planta.id
        db.session.commit()

        # Crear los rangos asociados a la planta
        nuevos_rangos = Rangos(
            id_planta=nueva_planta.id,
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
    modulo = ModuloEscolar.query.get_or_404(id)
    return render_template('show.html', modulo=modulo, rangos=modulo.planta.rangos if modulo.planta else None)

@main.route('/simulate/<int:id>')
def simulate(id):
    modulo = ModuloEscolar.query.get_or_404(id)
    rangos = modulo.planta.rangos if modulo.planta else None

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
    modulo = ModuloEscolar.query.get_or_404(id)
    
    # Eliminar la planta y sus rangos antes de eliminar el módulo
    if modulo.planta:
        if modulo.planta.rangos:
            db.session.delete(modulo.planta.rangos)
        db.session.delete(modulo.planta)

    db.session.delete(modulo)
    db.session.commit()

    flash("Módulo eliminado exitosamente.")
    return redirect(url_for('main.index'))
'''