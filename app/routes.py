# routes.py
from flask import Blueprint, render_template, request, g
from db import get_cassandra_cluster_and_session # Importa la configuracion de cassandra de db.py

main_bp = Blueprint('main', __name__)

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
