# routes.py
from flask import Blueprint, render_template, g
from db import get_cassandra_cluster_and_session # Importa la configuracion de cassadra de db.py

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