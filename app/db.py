from flask import g, current_app
from cassandra.cluster import Cluster
import os

def get_cassandra_cluster_and_session():
    if 'cassandra_cluster' not in g:
        try:
            # Variables obtenidas de .env
            cluster_hosts = current_app.config.get('CASSANDRA_HOSTS', ['127.0.0.1'])
            cluster_port = current_app.config.get('CASSANDRA_PORT', 9042)
            keyspace = current_app.config.get('CASSANDRA_KEYSPACE', 'app_music')

            g.cassandra_cluster = Cluster(cluster_hosts, port=cluster_port)
            g.cassandra_session = g.cassandra_cluster.connect(keyspace)
            print("Conectado a Cassandra de manera correcta (dentro del contexto de la app).")
        except Exception as e:
            print(f"Error al conectar a Cassandra: {e}")
            g.cassandra_cluster = None
            g.cassandra_session = None
    return g.cassandra_session, g.cassandra_cluster

def teardown_cassandra(exception):
    cluster = g.pop('cassandra_cluster', None)
    if cluster:
        cluster.shutdown()
        print("Conexión a Cassandra cerrada (al finalizar el contexto de la app).")