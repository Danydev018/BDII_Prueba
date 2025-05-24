# routes.py
from flask import Blueprint, render_template
from cassandra.cluster import Cluster

main_bp = Blueprint('main', __name__)

# Configuración de Cassandra
# posiblemente de mueva a .env
CASSANDRA_HOSTS = ['127.0.0.1']
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = 'app_music'

# funcion para optener la conexion a cassandra
def get_cassandra_session():
    """Establece la conexión a Cassandra y retorna la sesión."""
    try:
        cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
        session = cluster.connect(CASSANDRA_KEYSPACE)
        print("Conectado a Cassandra de manera correcta.")
        return session, cluster
    except Exception as e:
        print(f"Error al conectar a Cassandra: {e}")
        return None, None

# Ruta Principal
@main_bp.route("/")
def home():
    return render_template('index.html')

# Ruta que Muestra Usuario Registrados de la DB
@main_bp.route("/users")
def users_list():
    session, cluster = None, None
    users_data = []

    try:
        session, cluster = get_cassandra_session()
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
            # Trendremos que Hacer un HTML con este Error para harcelo mas atractivo
            return "<p>Error: No se pudo conectar a la base de datos de Cassandra.</p>"
    except Exception as e:
        return f"<p>Error al obtener datos: {e}</p>"
    finally:
        if cluster:
            cluster.shutdown()
            print("Conexión a Cassandra cerrada.")
