from flask import Flask, render_template # Importa render_template para usar plantillas HTML
from cassandra.cluster import Cluster

app = Flask(__name__) # Inicializa tu aplicación Flask

# Configuración de Cassandra (preferiblemente fuera de la ruta)
CASSANDRA_HOSTS = ['127.0.0.1']
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = 'app_music'

def get_cassandra_session():
    """Establece la conexión a Cassandra y retorna la sesión."""
    try:
        cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
        session = cluster.connect(CASSANDRA_KEYSPACE)
        print("Conectado a Cassandra de manera correcta.")
        return session, cluster # Retornamos también el cluster para cerrarlo después
    except Exception as e:
        print(f"Error al conectar a Cassandra: {e}")
        return None, None

@app.route("/")
def users_list():
    session, cluster = None, None
    users_data = [] # Lista para almacenar los datos de los usuarios

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
            return render_template('users.html', users=users_data) # Pasa los datos a una plantilla
        else:
            return "<p>Error: No se pudo conectar a la base de datos de Cassandra.</p>"
    except Exception as e:
        return f"<p>Error al obtener datos: {e}</p>"
    finally:
        if cluster:
            cluster.shutdown()
            print("Conexión a Cassandra cerrada.")

if __name__ == "__main__":
    app.run(debug=True) # Ejecuta la aplicación en modo depuración
