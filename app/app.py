# app.py
from flask import Flask
from routes import main_bp
from dotenv import load_dotenv
import os
from db import get_cassandra_cluster_and_session, teardown_cassandra # Importa El estado de cassandra y sus variables

# Cargara las variables del .env
load_dotenv()

app = Flask(__name__)

# Configuración de Cassandra (ahora se lee de las variables de entorno)
app.config['CASSANDRA_HOSTS'] = [os.getenv('CASSANDRA_HOSTS', '127.0.0.1')]
app.config['CASSANDRA_PORT'] = int(os.getenv('CASSANDRA_PORT', 9042))
app.config['CASSANDRA_KEYSPACE'] = os.getenv('CASSANDRA_KEYSPACE', 'app_music')

# Estado de Cassandra
app.teardown_appcontext(teardown_cassandra)

# Blueprint (Esta vaina e' para exportar las rutas)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)