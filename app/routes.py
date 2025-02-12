from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import ModuloEscolar, Planta, Rangos, Escuela, Variables, Dataloger, MedicionesBajadas
from app import db
from colegios import COLEGIOS
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from .api_client import obtener_datos


# Define el blueprint
main = Blueprint('main', __name__)

# -- TABLA MODULOS Y ENTIDADES --

@main.route('/')
def index():
    modulos = ModuloEscolar.query.all()  # Obtener todos los módulos
    return render_template('index.html', modulos=modulos)

# Crear un nuevo módulo escolar
@main.route('/modulos/crear', methods=['GET', 'POST'])
def modulos_crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ubicacion = request.form.get('ubicacion', None)
        coordenadas = request.form.get('coordenadas', None)
        id_escuela = request.form['escuela']
        id_dataloger = request.form['dataloger']
        id_planta = request.form['planta']

        nuevo_modulo = ModuloEscolar(
            nombre=nombre,
            ubicacion=ubicacion,
            coordenadas=coordenadas,
            id_escuela=id_escuela,
            id_dataloger=id_dataloger,
            id_planta=id_planta
        )

        db.session.add(nuevo_modulo)
        db.session.commit()
        flash("Módulo escolar creado correctamente", "success")
        return redirect(url_for('main.index'))

    escuelas = Escuela.query.all()
    datalogers = Dataloger.query.all()
    plantas = Planta.query.all()
    rangos = Rangos.query.all()

    return render_template('modulos_crear.html', escuelas=escuelas, datalogers=datalogers, plantas=plantas, rangos=rangos)

# Editar un módulo escolar
@main.route('/modulos/editar/<int:id>', methods=['GET', 'POST'])
def modulos_editar(id):
    modulo = ModuloEscolar.query.get_or_404(id)

    if request.method == 'POST':
        modulo.nombre = request.form['nombre']
        modulo.ubicacion = request.form.get('ubicacion', None)
        modulo.coordenadas = request.form.get('coordenadas', None)
        modulo.id_escuela = request.form['escuela']
        modulo.id_dataloger = request.form['dataloger']
        modulo.id_planta = request.form['planta']

        db.session.commit()
        flash("Módulo escolar actualizado correctamente", "success")
        return redirect(url_for('main.index'))

    escuelas = Escuela.query.all()
    datalogers = Dataloger.query.all()
    plantas = Planta.query.all()
    rangos = Rangos.query.all()

    return render_template('modulos_editar.html', modulo=modulo, escuelas=escuelas, datalogers=datalogers, plantas=plantas, rangos=rangos)


# -- TABLA ESCUELA --
@main.route('/escuelas')
def escuela_lista():
    escuelas = Escuela.query.all()  # Obtener todas las escuelas de la BD
    return render_template('escuela_lista.html', escuelas=escuelas)

@main.route('/escuela/crear', methods=['GET', 'POST'])
def escuela_crear():
    if request.method == 'POST':
        try:
            data = request.form  

            nombre = data.get("nombre")
            comuna = data.get("comuna")
            director = data.get("director")
            profesor = data.get("profesor")
            curso = data.get("curso")

            # Obtener información de la escuela desde COLEGIOS
            info_escuela = COLEGIOS.get(nombre)
            if not info_escuela:
                flash("Colegio no válido", "danger")
                return redirect(url_for('main.escuela_crear'))

            coordenadas_wkt = info_escuela["coordenadas"]

            # Convertir WKT a objeto POINT
            lon, lat = map(float, coordenadas_wkt.replace("POINT (", "").replace(")", "").strip().split())
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


# -- TABLA PLANTAS --
@main.route('/plantas')
def plantas_lista():
    plantas = Planta.query.all()
    return render_template('plantas_lista.html', plantas=plantas)

# Crear Planta
@main.route('/plantas/crear', methods=['GET', 'POST'])
def plantas_crear():
    if request.method == 'POST':
        especie = request.form['especie']
        fecha_plantado = request.form.get('fecha_plantado')
        fecha_cosecha = request.form.get('fecha_cosecha')

        # Crear la nueva planta
        nueva_planta = Planta(especie=especie, fecha_plantado=fecha_plantado, fecha_cosecha=fecha_cosecha)
        db.session.add(nueva_planta)
        db.session.commit()

        # Agregar rangos asociados
        for key in request.form:
            if key.startswith("temperatura_min_"):
                index = key.split("_")[-1]
                temperatura_min = request.form[f"temperatura_min_{index}"]
                temperatura_max = request.form[f"temperatura_max_{index}"]
                ph_min = request.form[f"ph_min_{index}"]
                ph_max = request.form[f"ph_max_{index}"]
                humedad_min = request.form[f"humedad_min_{index}"]
                humedad_max = request.form[f"humedad_max_{index}"]
                id_variable = request.form.get(f"variable_{index}")

                nuevo_rango = Rangos(
                    temperatura_min=temperatura_min,
                    temperatura_max=temperatura_max,
                    ph_min=ph_min,
                    ph_max=ph_max,
                    humedad_min=humedad_min,
                    humedad_max=humedad_max,
                    id_planta=nueva_planta.id,
                    id_variable=id_variable
                )
                db.session.add(nuevo_rango)
        
        db.session.commit()
        return redirect(url_for('main.plantas_lista'))

    variables = Variables.query.all()  # Asegúrate de que Variables está en tu modelo
    return render_template('plantas_crear.html', variables=variables)


# Editar Planta
@main.route('/plantas/editar/<int:id>', methods=['GET', 'POST'])
def plantas_editar(id):
    planta = Planta.query.get_or_404(id)
    rangos = Rangos.query.all()  # Obtener los rangos disponibles

    if request.method == 'POST':
        planta.especie = request.form['especie']
        planta.fecha_plantado = request.form['fecha_plantado'] or None
        planta.fecha_cosecha = request.form['fecha_cosecha'] or None

        db.session.commit()
        flash('Planta actualizada con éxito.', 'success')
        return redirect(url_for('main.plantas_lista'))

    return render_template('plantas_editar.html', planta=planta, rangos=rangos)

# Eliminar Planta
@main.route('/plantas/eliminar/<int:id>', methods=['POST'])
def plantas_eliminar(id):
    planta = Planta.query.get_or_404(id)
    db.session.delete(planta)
    db.session.commit()
    flash('Planta eliminada con éxito.', 'success')
    return redirect(url_for('main.plantas_lista'))


# -- TABLA VARIABLES --
@main.route('/variables', methods=['GET'])
def variables_lista():
    variables = Variables.query.all()
    return render_template('variables_lista.html', unidades=variables)  

@main.route('/variables/crear', methods=['GET', 'POST'])
def variables_crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        unidad_medida = request.form['abreviatura']  

        nueva_variable = Variables(nombre=nombre, unidad_medida=unidad_medida)
        db.session.add(nueva_variable)
        db.session.commit()

        flash("Variable creada correctamente", "success")
        return redirect(url_for('main.variables_lista'))

    return render_template('variables_crear.html')

@main.route('/variables/editar/<int:id>', methods=['GET', 'POST'])
def variables_editar(id):
    variable = Variables.query.get_or_404(id)

    if request.method == 'POST':
        variable.nombre = request.form['nombre']
        variable.unidad_medida = request.form['abreviatura']  # Asegurar que se use 'unidad_medida'

        db.session.commit()
        flash("Variable actualizada correctamente", "success")
        return redirect(url_for('main.variables_lista'))

    return render_template('variables_editar.html', variable=variable)

@main.route('/variables/eliminar/<int:id>', methods=['GET'])
def variables_eliminar(id):
    variable = Variables.query.get_or_404(id)
    db.session.delete(variable)
    db.session.commit()

    flash("Variable eliminada correctamente", "success")
    return redirect(url_for('main.variables_lista'))


# -- TABLA DATALOGER --

@main.route('/datalogers', methods=['GET'])
def datalogers_lista():
    datalogers = Dataloger.query.all()
    return render_template('datalogers_lista.html', datalogers=datalogers)


@main.route('/datalogers/crear', methods=['GET', 'POST'])
def datalogers_crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ip = request.form['ip']
        api_token = request.form['api_token']
        api_url = request.form['api_url']

        nuevo_dataloger = Dataloger(nombre=nombre, ip=ip, api_token=api_token, api_url=api_url)
        db.session.add(nuevo_dataloger)
        db.session.commit()

        flash("Dataloger creado correctamente", "success")
        return redirect(url_for('main.datalogers_lista'))

    return render_template('datalogers_crear.html')


@main.route('/datalogers/editar/<int:id>', methods=['GET', 'POST'])
def datalogers_editar(id):
    dataloger = Dataloger.query.get_or_404(id)

    if request.method == 'POST':
        dataloger.nombre = request.form['nombre']
        dataloger.ip = request.form['ip']
        dataloger.api_token = request.form['api_token']
        dataloger.api_url = request.form['api_url']

        db.session.commit()
        flash("Dataloger actualizado correctamente", "success")
        return redirect(url_for('main.datalogers_lista'))

    return render_template('datalogers_editar.html', dataloger=dataloger)


@main.route('/datalogers/eliminar/<int:id>', methods=['POST'])
def datalogers_eliminar(id):
    dataloger = Dataloger.query.get_or_404(id)
    db.session.delete(dataloger)
    db.session.commit()

    flash("Dataloger eliminado correctamente", "success")
    return redirect(url_for('main.datalogers_lista'))






# -- API -- 
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