# routes.py
from flask import Blueprint, render_template, request, g
from db import get_cassandra_cluster_and_session # Importa la configuracion de cassandra de db.py
from datetime import datetime
main_bp = Blueprint('main', __name__)

# Helper to convert month number to name (can be moved to a utility file if preferred)
# Corrected month_names dictionary
month_names = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def format_escuchas(num):
    if num is None:
        return "0"
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}k"
    else:
        return str(num)
    
# Ruta Principal
@main_bp.route("/")
def home():
    session, cluster = get_cassandra_cluster_and_session()
    novedades = []
    destacados = []
    try:
        if session:
            # Canciones del presente año para Novedades
            current_year = datetime.now().year
            rows_novedades = session.execute(
                "SELECT cancion_id, titulo, artista, genero, anio FROM recomendaciones WHERE anio = %s ALLOW FILTERING",
                (current_year,)
            )
            novedades = [
                {
                    'titulo': row.titulo,
                    'artista': row.artista,
                    'genero': row.genero,
                    'anio': row.anio
                }
                for row in rows_novedades
            ][:3]

            # Tres canciones más escuchadas para Destacado
            rows_destacados = session.execute(
                "SELECT cancion_id, titulo, artista, genero, anio, total_escuchas FROM recomendaciones"
            )
            canciones_ordenadas = sorted(rows_destacados, key=lambda r: r.total_escuchas if r.total_escuchas else 0, reverse=True)
            destacados = [
                {
                    'titulo': row.titulo,
                    'artista': row.artista,
                    'genero': row.genero,
                    'anio': row.anio,
                    'escuchas': format_escuchas(row.total_escuchas)
                }
                for row in canciones_ordenadas
            ][:3]

        return render_template('index.html', novedades=novedades, destacados=destacados)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<p>Error al obtener datos para la página principal: {e}</p>"

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
    top_songs = []

    try:
        if session:
            # 1. Get monthly listens for the genre (existing logic)
            query_monthly_listens = "SELECT anio, mes, total_escuchas FROM escuchas_por_genero_y_mes WHERE genero = %s ALLOW FILTERING"
            rows_monthly = session.execute(query_monthly_listens, (genre_name,))

            for row in rows_monthly:
                monthly_listens.append({
                    'anio': row.anio,
                    'mes': row.mes,
                    'mes_nombre': month_names.get(row.mes, 'Desconocido'), # Use corrected month_names
                    'total_escuchas': row.total_escuchas
                })
            monthly_listens.sort(key=lambda x: (x['anio'], x['mes']))

            # 2. Get Top 5 songs for the genre
            # 2a. Find all songs in the given genre
            query_songs_in_genre = "SELECT cacion_id, titulo, artista FROM song WHERE genero = %s ALLOW FILTERING"
            songs_in_genre = session.execute(query_songs_in_genre, (genre_name,))
            
            song_listen_counts = []

            for song_row in songs_in_genre:
                total_listens_for_song = 0
                # 2b. For each song, sum its listens from canciones_escuchadas_por_mes
                query_song_listens = "SELECT total_escuchadas FROM canciones_escuchadas_por_mes WHERE id_cancion = %s ALLOW FILTERING"
                listen_records = session.execute(query_song_listens, (song_row.cacion_id,))
                
                for listen_record in listen_records:
                    total_listens_for_song += listen_record.total_escuchadas
                
                if total_listens_for_song > 0:
                    song_listen_counts.append({
                        'nombre_cancion': song_row.titulo,
                        'artista': song_row.artista,
                        'total_escuchas': total_listens_for_song
                    })
            
            # 2c. Sort songs by total listens and get the top 5
            top_songs = sorted(song_listen_counts, key=lambda x: x['total_escuchas'], reverse=True)[:5]

            return render_template('genre_detail.html', 
                                   genre_name=genre_name, 
                                   monthly_listens=monthly_listens,
                                   top_songs=top_songs)
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
        
        # Filtro para las 10 canciones más escuchadas globalmente
        if filtro == "mas_escuchadas":
            rows = session.execute(
                "SELECT cancion_id, anio, genero, artista, titulo, total_escuchas FROM recomendaciones"
            )
            # Ordena por total_escuchas y limita a 10
            canciones = sorted(rows, key=lambda r: r.total_escuchas if r.total_escuchas else 0, reverse=True)[:10]
            recomendaciones = [
                {
                    'titulo': row.titulo,
                    'artista': row.artista,
                    'genero': row.genero,
                    'anio': row.anio,
                    'escuchas': row.total_escuchas
                }
                for row in canciones
            ]
            return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
        
        
        
        # Filtro para las 10 canciones menos escuchadas globalmente
        if filtro == "menos_escuchadas":
            rows = session.execute(
                "SELECT cancion_id, anio, genero, artista, titulo, total_escuchas FROM recomendaciones"
            )
            # Ordena por total_escuchas ascendente y limita a 10
            canciones = sorted(rows, key=lambda r: r.total_escuchas if r.total_escuchas is not None else 0)[:10]
            recomendaciones = [
                {
                    'titulo': row.titulo,
                    'artista': row.artista,
                    'genero': row.genero,
                    'anio': row.anio,
                    'escuchas': row.total_escuchas
                }
                for row in canciones
            ]
            return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
        
        
        
        # Filtro para las 10 canciones más recientes (por año)
        if filtro == "recientes":
            rows = session.execute(
                "SELECT cancion_id, anio, genero, artista, titulo, total_escuchas FROM recomendaciones"
            )
            # Ordena por anio descendente y limita a 10
            canciones = sorted(rows, key=lambda r: r.anio if r.anio else 0, reverse=True)[:10]
            recomendaciones = [
                {
                    'titulo': row.titulo,
                    'artista': row.artista,
                    'genero': row.genero,
                    'anio': row.anio,
                    'escuchas': row.total_escuchas
                }
                for row in canciones
            ]
            return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
        
        
        
        # Filtro para las 10 canciones más antiguas (por año)
        if filtro == "antiguas":
            rows = session.execute(
                "SELECT cancion_id, anio, genero, artista, titulo, total_escuchas FROM recomendaciones"
            )
            # Ordena por anio ascendente y limita a 10
            canciones = sorted(rows, key=lambda r: r.anio if r.anio else 0)[:10]
            recomendaciones = [
                {
                    'titulo': row.titulo,
                    'artista': row.artista,
                    'genero': row.genero,
                    'anio': row.anio,
                    'escuchas': row.total_escuchas
                }
                for row in canciones
            ]
            return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
        
        
        
        if filtro == "genero":
            genero = request.args.get('genero', '').strip()
            print(f"""El género seleccionado es: {genero}""")
            if genero:
                # Consulta la tabla recomendaciones por género
                rows = session.execute(
                    "SELECT cancion_id, anio, genero, artista, titulo, total_escuchas FROM recomendaciones WHERE genero = %s ALLOW FILTERING",
                    (genero,)
                )
                # Ordena por total_escuchas y limita a 20
                canciones = sorted(rows, key=lambda r: r.total_escuchas if r.total_escuchas else 0, reverse=True)[:20]
                recomendaciones = [
                    {
                        'titulo': row.titulo,
                        'artista': row.artista,
                        'genero': row.genero,
                        'anio': row.anio,
                        'escuchas': row.total_escuchas
                    }
                    for row in canciones
                ]
                return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
            
            
            
        #Logica para el filtro de año
        if filtro == "anio":
            anio = request.args.get('anio', '').strip()
            print(f"""El año seleccionado es: {anio}""")
            if anio:
                # Consulta la tabla recomendaciones por año
                rows = session.execute(
                    "SELECT cancion_id, anio, genero, artista, titulo, total_escuchas FROM recomendaciones WHERE anio = %s ALLOW FILTERING",
                    (int(anio),)
                )
                # Ordena por total_escuchas y limita a 15
                canciones = sorted(rows, key=lambda r: r.total_escuchas if r.total_escuchas else 0, reverse=True)[:15]
                recomendaciones = [
                    {
                        'titulo': row.titulo,
                        'artista': row.artista,
                        'genero': row.genero,
                        'anio': row.anio,
                        'escuchas': row.total_escuchas
                    }
                    for row in canciones
                ]
                return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
        
            
            
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
        if filtro == "artista":
            # Obtener los últimos 3 artistas escuchados
            canciones_ordenadas = sorted(canciones, key=lambda x: x['fecha_escucha'], reverse=True)
            artistas_recientes = []
            for c in canciones_ordenadas:
                if c['artista'] and c['artista'] not in artistas_recientes:
                    artistas_recientes.append(c['artista'])
                if len(artistas_recientes) == 3:
                    break

            # Última canción escuchada de cada artista
            canciones_filtradas = []
            canciones_extra = []
            canciones_por_artista = {artista: [] for artista in artistas_recientes}
            for c in canciones_ordenadas:
                if c['artista'] in artistas_recientes:
                    canciones_por_artista[c['artista']].append(c)

            # Agrega la última canción escuchada de cada artista
            for artista in artistas_recientes:
                if canciones_por_artista[artista]:
                    canciones_filtradas.append(canciones_por_artista[artista][0])

            # Agrega hasta dos canciones adicionales por artista (sin repetir la última ya agregada)
            for artista in artistas_recientes:
                adicionales = canciones_por_artista[artista][1:3]  # máximo dos más
                canciones_extra.extend(adicionales)
                
            canciones = canciones_filtradas + canciones_extra
        
        recomendaciones = canciones

        return render_template('recomendaciones.html', usuario=usuario, recomendaciones=recomendaciones)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<p>Error al obtener recomendaciones: {e}</p>"