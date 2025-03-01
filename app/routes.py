from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models import ModuloEscolar, Planta, Rangos, Escuela, Variables, Dataloger, MedicionesBajadas
from app import db
from colegios import COLEGIOS
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from .api_client import obtener_datos
from sqlalchemy import func
import random


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
# Obtener escuelas con coordenadas en formato correcto (WKT)
    escuelas = Escuela.query.with_entities(
        Escuela.id, 
        Escuela.nombre, 
        db.func.ST_AsText(Escuela.coordenadas).label("coordenadas")
    ).all()
    datalogers = Dataloger.query.all()
    plantas = Planta.query.all()
    rangos = Rangos.query.all()

    if request.method == 'POST':
        nombre = request.form['nombre']
        ubicacion = request.form.get('ubicacion', None)
        coordenadas = f"POINT({request.form.get('coordenadas', '')})"
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

        flash(f"<b>{nuevo_modulo.nombre}</b> agregado con éxito.", "success")  # 🟢 Aquí agregamos el nombre en negritas
        return redirect(url_for('main.index'))

    return render_template(
        'modulos_crear.html',
        escuelas=escuelas,
        datalogers=datalogers,
        plantas=plantas,
        rangos=rangos
    )

# Editar un módulo escolar
@main.route('/modulos/editar/<int:id>', methods=['GET', 'POST'])
def modulos_editar(id):
    modulo = ModuloEscolar.query.get_or_404(id)  # Obtenemos el objeto modificable

    # Convertir coordenadas a formato WKT
    coordenadas_wkt = db.session.query(
        db.func.ST_AsText(ModuloEscolar.coordenadas)
    ).filter(ModuloEscolar.id == id).scalar()

    if request.method == 'POST':
        modulo.nombre = request.form['nombre']
        modulo.ubicacion = request.form.get('ubicacion', None)
        coordenadas = request.form.get('coordenadas', None)
        if coordenadas:
            modulo.coordenadas = func.ST_GeomFromText(f"POINT({coordenadas})")
        modulo.id_escuela = request.form['escuela']
        modulo.id_dataloger = request.form['dataloger']
        modulo.id_planta = request.form['planta']

        db.session.commit()
        flash(f"<b>{modulo.nombre}</b> ctualizado correctamente.", "success")  # 🟢 Aquí agregamos el nombre en negritas

        return redirect(url_for('main.index'))

    escuelas = Escuela.query.all()
    datalogers = Dataloger.query.all()
    plantas = Planta.query.all()
    rangos = Rangos.query.all()

    return render_template(
        'modulos_editar.html',
        modulo=modulo,
        escuelas=escuelas,
        datalogers=datalogers,
        plantas=plantas,
        rangos=rangos,
        coordenadas_wkt=coordenadas_wkt  # <-- Asegúrate de pasarlo a la plantilla
    )

@main.route('/modulos/eliminar/<int:id>', methods=['POST'])
def modulos_eliminar(id):
    modulo = ModuloEscolar.query.get_or_404(id)

    try:
        db.session.delete(modulo)
        db.session.commit()
        flash(f'El módulo {modulo.nombre} ha sido eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el módulo: {str(e)}', 'danger')

    return redirect(url_for('main.index'))


@main.route('/modulos/simulacion/<int:id>', methods=['GET'])
def modulos_simulacion(id):
    modulo = ModuloEscolar.query.get_or_404(id)
    planta = Planta.query.get_or_404(modulo.id_planta)

    # Obtener los rangos de la planta
    rangos = Rangos.query.filter_by(id_planta=planta.id).first()   

    if rangos is None:
        flash("No hay rangos definidos para esta planta.", "warning")
        return redirect(url_for("main.index"))  # Reemplaza con la ruta correcta

    # 🔹 Obtener unidades desde la base de datos (si Rangos tiene relación con Variables)
    variables = {
        "Temperatura": Variables.query.filter_by(nombre="Temperatura").first(),
        "pH": Variables.query.filter_by(nombre="pH").first(),
        "Humedad": Variables.query.filter_by(nombre="Humedad").first()
    }

    # 🔹 Crear diccionario de rangos con unidades de medida
    rangos_dict = {
        "Temperatura": {
            "min": rangos.temperatura_min if rangos.temperatura_min is not None else 15.0,
            "max": rangos.temperatura_max if rangos.temperatura_max is not None else 30.0,
            "unidad": variables["Temperatura"].unidad if variables["Temperatura"] else "°C"
        },
        "pH": {
            "min": rangos.ph_min if rangos.ph_min is not None else 6.0,
            "max": rangos.ph_max if rangos.ph_max is not None else 7.5,
            "unidad": variables["pH"].unidad if variables["pH"] else "pH"
        },
        "Humedad": {
            "min": rangos.humedad_min if rangos.humedad_min is not None else 40.0,
            "max": rangos.humedad_max if rangos.humedad_max is not None else 80.0,
            "unidad": variables["Humedad"].unidad if variables["Humedad"] else "%"
        }
    }

    # 🔹 Generar valores simulados
    valores_simulados = {
        "Temperatura": round(random.uniform(rangos_dict["Temperatura"]["min"] - 5, rangos_dict["Temperatura"]["max"] + 5), 1),
        "pH": round(random.uniform(rangos_dict["pH"]["min"] - 2, rangos_dict["pH"]["max"] + 2), 1),
        "Humedad": round(random.uniform(rangos_dict["Humedad"]["min"] - 10, rangos_dict["Humedad"]["max"] + 10), 1)
    }

    # 🔹 Determinar el estado de la planta
# 🔹 Determinar el estado de la planta
    num_alertas = 0
    num_precauciones = 0

    for var, valores in rangos_dict.items():
        if valores_simulados[var] < valores["min"] or valores_simulados[var] > valores["max"]:
            num_alertas += 1
        elif abs(valores_simulados[var] - valores["min"]) <= 2 or abs(valores_simulados[var] - valores["max"]) <= 2:
            num_precauciones += 1

    # 🔹 Nueva lógica de color basada en el número de alertas/precauciones
    if num_alertas + num_precauciones == 3:  
        estado_color = "red"     # Todas las variables en alerta o precaución
    elif num_alertas + num_precauciones == 2:  
        estado_color = "orange"  # Dos variables en alerta/precaución
    elif num_alertas + num_precauciones == 1:  
        estado_color = "yellow"  # Solo una variable en alerta/precaución
    else:  
        estado_color = "green"   # Todo en orden
    
    return render_template("modulos_simulacion.html", modulo=modulo, planta=planta, valores_simulados=valores_simulados, estado_color=estado_color, rangos_dict=rangos_dict, abs=abs)

@main.route('/modulos/simulacion_ajax/<int:id>', methods=['GET'])
def modulos_simulacion_ajax(id):
    modulo = ModuloEscolar.query.get_or_404(id)
    planta = Planta.query.get_or_404(modulo.id_planta)

    rangos = Rangos.query.filter_by(id_planta=planta.id).first()
    if rangos is None:
        return jsonify({"error": "No hay rangos definidos para esta planta"}), 400

    variables = {
        "Temperatura": Variables.query.filter_by(nombre="Temperatura").first(),
        "pH": Variables.query.filter_by(nombre="pH").first(),
        "Humedad": Variables.query.filter_by(nombre="Humedad").first()
    }

    rangos_dict = {
        "Temperatura": {
            "min": rangos.temperatura_min or 15.0,
            "max": rangos.temperatura_max or 30.0,
            "unidad": variables["Temperatura"].unidad if variables["Temperatura"] else "°C"
        },
        "pH": {
            "min": rangos.ph_min or 6.0,
            "max": rangos.ph_max or 7.5,
            "unidad": variables["pH"].unidad if variables["pH"] else "pH"
        },
        "Humedad": {
            "min": rangos.humedad_min or 40.0,
            "max": rangos.humedad_max or 80.0,
            "unidad": variables["Humedad"].unidad if variables["Humedad"] else "%"
        }
    }

    valores_simulados = {
        "Temperatura": round(random.uniform(rangos_dict["Temperatura"]["min"] - 5, rangos_dict["Temperatura"]["max"] + 5), 1),
        "pH": round(random.uniform(rangos_dict["pH"]["min"] - 2, rangos_dict["pH"]["max"] + 2), 1),
        "Humedad": round(random.uniform(rangos_dict["Humedad"]["min"] - 10, rangos_dict["Humedad"]["max"] + 10), 1)
    }

    # Determinar el estado de la planta
    num_alertas = sum(1 for var, valores in rangos_dict.items() if valores_simulados[var] < valores["min"] or valores_simulados[var] > valores["max"])
    num_precauciones = sum(1 for var, valores in rangos_dict.items() if abs(valores_simulados[var] - valores["min"]) <= 2 or abs(valores_simulados[var] - valores["max"]) <= 2)

    if num_alertas + num_precauciones == 3:
        estado_color = "red"
    elif num_alertas + num_precauciones == 2:
        estado_color = "orange"
    elif num_alertas + num_precauciones == 1:
        estado_color = "yellow"
    else:
        estado_color = "green"

    return jsonify({
        "valores_simulados": valores_simulados,
        "estado_color": estado_color
    })



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

            flash(f"Escuela <b>{nombre}</b> creada correctamente", "success")  # 🔥 Mensaje en negritas
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
        flash(f"Escuela <b>{escuela.nombre}</b> actualizada correctamente", "success")  # 🔥 Mensaje en negritas
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

@main.route('/plantas/crear', methods=['GET', 'POST'])
def plantas_crear():
    if request.method == 'POST':
        especie = request.form['especie']
        fecha_plantado = request.form.get('fecha_plantado') or None
        fecha_cosecha = request.form.get('fecha_cosecha') or None

        # Crear la planta primero
        nueva_planta = Planta(
            especie=especie, 
            fecha_plantado=fecha_plantado, 
            fecha_cosecha=fecha_cosecha
        )
        db.session.add(nueva_planta)
        db.session.commit()  # Guardamos para obtener el ID de la planta

        # Obtener los valores de las variables
        id_variable_temp = request.form.get("variable_temp")
        id_variable_ph = request.form.get("variable_ph")
        id_variable_humedad = request.form.get("variable_humedad")

        # Crear un solo registro en Rangos con todos los valores
        nuevo_rango = Rangos(
            id_planta=nueva_planta.id,
            temperatura_min=float(request.form.get("temperatura_min")) if request.form.get("temperatura_min") else None,
            temperatura_max=float(request.form.get("temperatura_max")) if request.form.get("temperatura_max") else None,
            ph_min=float(request.form.get("ph_min")) if request.form.get("ph_min") else None,
            ph_max=float(request.form.get("ph_max")) if request.form.get("ph_max") else None,
            humedad_min=float(request.form.get("humedad_min")) if request.form.get("humedad_min") else None,
            humedad_max=float(request.form.get("humedad_max")) if request.form.get("humedad_max") else None
        )
        db.session.add(nuevo_rango)

        # Asignar variables a la planta en la tabla intermedia
        if id_variable_temp:
            nueva_planta.variables.append(Variables.query.get(int(id_variable_temp)))
        if id_variable_ph:
            nueva_planta.variables.append(Variables.query.get(int(id_variable_ph)))
        if id_variable_humedad:
            nueva_planta.variables.append(Variables.query.get(int(id_variable_humedad)))

        db.session.commit()  # Guardar todos los cambios en la base de datos

        flash(f"Planta <b>{especie}</b> y rangos agregados con éxito.", "success")  # 🟢 Aquí agregamos el nombre en negritas

        return redirect(url_for('main.plantas_lista'))

    variables = Variables.query.all()
    return render_template('plantas_crear.html', variables=variables)

@main.route('/plantas/editar/<int:id>', methods=['GET', 'POST'])
def plantas_editar(id):
    planta = Planta.query.get_or_404(id)
    variables = Variables.query.all()

    # Obtener rangos existentes o definir valores por defecto
    rango = Rangos.query.filter_by(id_planta=planta.id).first()
    if not rango:
        rango = Rangos(temperatura_min=0, temperatura_max=0, ph_min=0, ph_max=0, humedad_min=0, humedad_max=0)

    if request.method == 'POST':
        planta.especie = request.form['especie']
        planta.fecha_plantado = request.form.get('fecha_plantado') or None
        planta.fecha_cosecha = request.form.get('fecha_cosecha') or None

        id_variables = set(map(int, request.form.getlist('id_variables')))
        planta.variables = Variables.query.filter(Variables.id.in_(id_variables)).all()

        # Actualizar o crear el registro de Rangos
        rango = Rangos.query.filter_by(id_planta=planta.id).first()
        if not rango:
            rango = Rangos(id_planta=planta.id)  # Crear nuevo si no existe
            db.session.add(rango)

        rango.temperatura_min = request.form['temperatura_min']
        rango.temperatura_max = request.form['temperatura_max']
        rango.ph_min = request.form['ph_min']
        rango.ph_max = request.form['ph_max']
        rango.humedad_min = request.form['humedad_min']
        rango.humedad_max = request.form['humedad_max']

        # Guardar cambios
        db.session.commit()

        flash(f"Planta <b>{planta.especie}</b> actualizada con éxito.", "success")  # 🟢 Aquí agregamos el nombre en negritas
        return redirect(url_for('main.plantas_lista'))


    variables_seleccionadas = [v.id for v in planta.variables]
    
    return render_template('plantas_editar.html', planta=planta, variables=variables, variables_seleccionadas=variables_seleccionadas, rango=rango)

# Eliminar Planta
@main.route('/plantas/eliminar/<int:id>', methods=['POST'])
def plantas_eliminar(id):
    planta = Planta.query.get_or_404(id)

    try:
        # Eliminar los rangos asociados a la planta
        Rangos.query.filter_by(id_planta=planta.id).delete()

        # Desvincular variables de la planta antes de eliminar
        planta.variables.clear()
        db.session.commit()

        # Ahora eliminar la planta
        db.session.delete(planta)
        db.session.commit()

        flash('Planta y sus rangos eliminados con éxito.', 'success')
        return '', 204  # Respuesta exitosa sin contenido

    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la planta. Verifique dependencias.', 'danger')
        return '', 400  # Código de error

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

        flash(f"Variable <b>{nombre}</b> creada correctamente", "success")  # 🟢 Aquí agregamos el nombre en negritas
        return redirect(url_for('main.variables_lista'))

    return render_template('variables_crear.html')

@main.route('/variables/editar/<int:id>', methods=['GET', 'POST'])
def variables_editar(id):
    variable = Variables.query.get_or_404(id)

    if request.method == 'POST':
        variable.nombre = request.form['nombre']
        variable.unidad_medida = request.form['abreviatura']  

        db.session.commit()
        flash(f"Variable <b>{variable.nombre}</b> actualizada correctamente", "success")  # 🟢 Aquí también
        return redirect(url_for('main.variables_lista'))

    return render_template('variables_editar.html', variable=variable)

@main.route('/variables/eliminar/<int:id>', methods=['POST'])
def variables_eliminar(id):
    variable = Variables.query.get_or_404(id)
    
    try:
        db.session.delete(variable)
        db.session.commit()
        flash("Variable eliminada correctamente", "success")
        return '', 204  # Respuesta vacía con código 204 (No Content)
    
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar la variable. Puede estar en uso.", "danger")
        return '', 400  # Código de error HTTP 400 (Bad Request)


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

        flash(f"Dataloger <b>{nombre}</b> creado correctamente", "success")  # 🔥 Usamos flash() aquí
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
        flash(f"Dataloger <b>{dataloger.nombre}</b> actualizado correctamente", "success")  # 🔥 También aquí
        return redirect(url_for('main.datalogers_lista'))

    return render_template('datalogers_editar.html', dataloger=dataloger)

@main.route('/datalogers/eliminar/<int:id>', methods=['POST'])
def datalogers_eliminar(id):
    datalogger = Dataloger.query.get_or_404(id)
    
    try:
        db.session.delete(datalogger)
        db.session.commit()
        flash("Dataloger eliminado correctamente", "success")
        return '', 204  # Éxito sin contenido
    
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar el Dataloger. Puede estar en uso.", "danger")
        return '', 400  # Error en la solicitud



# -- LIMPIAR MENSAJES SWEETALERT2 -- 
@main.route('/limpiar-mensajes', methods=['POST'])
def limpiar_mensajes():
    session.pop('mensaje', None)
    session.pop('categoria', None)
    return '', 204  # Respuesta vacía con código 204 (No Content)



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