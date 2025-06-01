# routes.py
from flask import Blueprint, render_template, request, g
from db import get_cassandra_cluster_and_session # Importa la configuracion de cassandra de db.py

main_bp = Blueprint('main', __name__)

# Helper to convert month number to name (can be moved to a utility file if preferred)
month_names = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Noviembre', 11: 'Diciembre'
}

# Ruta Principal
@main_bp.route("/")
def home():
    return render_template('index.html')

# Ruta que Muestra Usuario Registrados de la DB
@main_bp.route("/users")
def users_list():
    session, cluster = get_cassandra_cluster_and_session()

    users_data = []

    try:
        if session:
            rows = session.execute("SELECT usuario_id, ciudad, nombre FROM users")
            for row in rows:
                users_data.append({
                    'usuario_id': row.usuario_id,
                    'nombre': row.nombre,
                    'ciudad': row.ciudad
                    })
            return render_template('users.html', users=users_data)
        else:
            return "<p>Error: No se pudo conectar a la base de datos de Cassandra.</p>"
    except Exception as e:
        return f"<p>Error al obtener datos: {e}</p>"

# Nueva Ruta para Buscar Canciones
@main_bp.route("/search_songs", methods=['GET'])
def search_songs():
    search_query = request.args.get('query', '').strip() # Get the 'query' parameter from the URL

    session, cluster = get_cassandra_cluster_and_session()
    song_data = []

    try:
        if session:
            if search_query:
                # Use ALLOW FILTERING for demonstration, but for production, consider denormalization or SASI index
                # on 'title' for better performance.
                rows = session.execute(
                        "SELECT cacion_id, titulo, artista, genero FROM song WHERE titulo LIKE %s ALLOW FILTERING", (f"%{search_query}%",) )
                for row in rows:
                    song_data.append({
                        'song_id': row.cacion_id,
                        'title': row.titulo,
                        'artist': row.artista,
                        'genre': row.genero,
                        })
            return render_template('search_results.html', query=search_query, songs=song_data)
        else:
            return "<p>Error: No se pudo conectar a la base de datos de Cassandra.</p>"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<p>Error al realizar la búsqueda: {e}</p>"

# Nueva Ruta para Detalle de Género
@main_bp.route('/genre/<genre_name>')
def genre_detail(genre_name):
    session, cluster = get_cassandra_cluster_and_session()
    monthly_listens = []

    try:
        if session:
            query = "SELECT anio, mes, total_escuchas FROM escuchas_por_genero_y_mes WHERE genero = %s ALLOW FILTERING"
            rows = session.execute(query, (genre_name,))

            for row in rows:
                monthly_listens.append({
                    'anio': row.anio,
                    'mes': row.mes,
                    'mes_nombre': month_names.get(row.mes, 'Desconocido'),
                    'total_escuchas': row.total_escuchas
                })

            # Sort by year and then month for better presentation
            monthly_listens.sort(key=lambda x: (x['anio'], x['mes']))

            return render_template('genre_detail.html', genre_name=genre_name, monthly_listens=monthly_listens)
        else:
            return "<p>Error: No se pudo conectar a la base de datos de Cassandra.</p>"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<p>Error al obtener detalles del género: {e}</p>"



@main_bp.route("/recomendaciones")
def recomendaciones():
    session, cluster = get_cassandra_cluster_and_session()
    usuario = request.args.get('usuario', '').strip()
    filtro = request.args.get('filtro', '').strip()
    recomendaciones = []
    
    print(f"Usuario recibido: '{usuario}'") 

    if not usuario:
        return render_template('recomendaciones.html', usuario=None, recomendaciones=None)

    try:
        # 1a Buscar usuario_id por nombre
        user_row = session.execute(
            "SELECT usuario_id FROM users WHERE nombre = %s ALLOW FILTERING", (usuario,)
        ).one()
        if not user_row:
            # Prueba búsqueda insensible a mayúsculas
            rows = session.execute("SELECT usuario_id, nombre FROM users ALLOW FILTERING")
            for row in rows:
                print(f"Comparando '{row.nombre.strip().lower()}' con '{usuario.lower()}'")
                if row.nombre.strip().lower() == usuario.lower():
                    user_row = row
                    break
            print(f"Resultado user_row (fallback): {user_row}") 

        if not user_row:
            return render_template('recomendaciones.html', usuario=usuario, recomendaciones=None)


        usuario_id = user_row.usuario_id
        print(f"usuario_id encontrado: {usuario_id}")
        
        
        # Lógica especial para el filtro "ciudad"
        if filtro == "ciudad":
            # 1b. Obtener la ciudad del usuario
            user_info = session.execute(
                "SELECT ciudad FROM users WHERE usuario_id = %s", (usuario_id,)
            ).one()
            if not user_info:
                return render_template('recomendaciones.html', usuario=usuario, recomendaciones=[])
            ciudad_usuario = user_info.ciudad

            # 2b. Obtener todos los usuarios de esa ciudad, EXCLUYENDO al usuario actual
            usuarios_ciudad = [
                row.usuario_id for row in session.execute(
                    "SELECT usuario_id FROM users WHERE ciudad = %s ALLOW FILTERING", (ciudad_usuario,)
                ) if row.usuario_id != usuario_id
            ]
            if not usuarios_ciudad:
                return render_template('recomendaciones.html', usuario=usuario, recomendaciones=[])

            # 3b. Contar escuchas de cada canción por todos los usuarios de esa ciudad (sin el usuario actual)
            canciones_dict = {}
            for uid in usuarios_ciudad:
                listen_rows = session.execute(
                    "SELECT cacion_id FROM listen_song_by_user WHERE usuario_id = %s", (uid,)
                )
                for row in listen_rows:
                    if row.cacion_id not in canciones_dict:
                        canciones_dict[row.cacion_id] = 1
                    else:
                        canciones_dict[row.cacion_id] += 1

            # 4b. Obtener detalles de las canciones y armar la lista
            canciones = []
            for cacion_id, total in sorted(canciones_dict.items(), key=lambda x: x[1], reverse=True):
                song_row = session.execute(
                    "SELECT titulo, artista, genero, anho FROM song WHERE cacion_id = %s", (cacion_id,)
                ).one()
                if song_row:
                    canciones.append({
                        'titulo': song_row.titulo,
                        'artista': song_row.artista,
                        'genero': song_row.genero,
                        'anio': song_row.anho,
                        'fecha_escucha': None,
                        'ciudad': ciudad_usuario,
                        'escuchas': total
                    })
            recomendaciones = canciones
            return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
        
        ## Continua logica inicial si no se requiere el filtro por ciudad

        # 2a. Obtener escuchas del usuario
        listen_rows = session.execute(
            "SELECT cacion_id, fecha_escucha FROM listen_song_by_user WHERE usuario_id = %s", (usuario_id,)
        )

        # 3a. Obtener detalles de canciones escuchadas
        canciones_dict = {}
        for row in listen_rows:
            song_row = session.execute(
                "SELECT titulo, artista, genero, anho FROM song WHERE cacion_id = %s", (row.cacion_id,)
            ).one()
            if song_row:
                # Obtener ciudad del usuario si se requiere para el filtro
                ciudad = None
                if filtro == "ciudad":
                    user_info = session.execute(
                        "SELECT ciudad FROM users WHERE usuario_id = %s", (usuario_id,)
                    ).one()
                    ciudad = user_info.ciudad if user_info else None

                # Contar escuchas de la canción por el usuario
                escuchas_count = session.execute(
                    "SELECT COUNT(*) as total FROM listen_song_by_user WHERE usuario_id = %s AND cacion_id = %s ALLOW FILTERING",
                    (usuario_id, row.cacion_id)
                ).one().total
                
                if row.cacion_id in canciones_dict:
                    if row.fecha_escucha > canciones_dict[row.cacion_id]['fecha_escucha']:
                        canciones_dict[row.cacion_id]['fecha_escucha'] = row.fecha_escucha


                else:
                    canciones_dict[row.cacion_id] = {
                        'titulo': song_row.titulo,
                        'artista': song_row.artista,
                        'genero': song_row.genero,
                        'anio': song_row.anho,
                        'fecha_escucha': row.fecha_escucha,
                        'ciudad': ciudad,
                        'escuchas': escuchas_count
                    }
        canciones = list(canciones_dict.values())

        # 4a. Aplicar filtro
        if filtro == "recientes":
            canciones.sort(key=lambda x: x['fecha_escucha'], reverse=True)
        elif filtro == "antiguas":
            canciones.sort(key=lambda x: x['fecha_escucha'])
        elif filtro == "genero":
            canciones.sort(key=lambda x: x['genero'])
        elif filtro == "artista":
            canciones.sort(key=lambda x: x['artista'])
        elif filtro == "titulo":
            canciones.sort(key=lambda x: x['titulo'])
        elif filtro == "recientes":
            canciones.sort(key=lambda x: x['anio'] if x['anio'] else 0, reverse=True)
        elif filtro == "antiguas":
            canciones.sort(key=lambda x: x['anio'] if x['anio'] else 0)
        elif filtro == "mes":
            canciones.sort(key=lambda x: x['fecha_escucha'].month if x['fecha_escucha'] else 0)
        elif filtro == "ciudad":
            canciones.sort(key=lambda x: x['ciudad'] if x['ciudad'] else "")
        elif filtro == "escuchas":
            canciones.sort(key=lambda x: x['escuchas'], reverse=True)
        elif filtro == "mas_escuchadas":
            canciones.sort(key=lambda x: x['escuchas'], reverse=True)
        elif filtro == "menos_escuchadas":
            canciones.sort(key=lambda x: x['escuchas'])

        recomendaciones = canciones

        return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<p>Error al obtener recomendaciones: {e}</p>"
