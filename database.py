from cassandra.cluster import Cluster

def create_cassandra_schema_no_auth(
    contact_points=['127.0.0.1'],  # IP(s) de tu nodo(s) de Cassandra
    port=9042,
    keyspace_name='prueba',
    replication_factor=1
):
    """
    Crea una keyspace y tablas en Cassandra.
    """
    cluster = None
    session = None
    try:
        cluster = Cluster(contact_points, port=port)
        session = cluster.connect()
        print(f"Conectado a Cassandra en {contact_points[0]}:{port} (sin autenticación).")

        # 1. Crear la Keyspace
        create_keyspace_query = f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace_name}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': {replication_factor}}};
        """
        session.execute(create_keyspace_query)
        print(f"Keyspace '{keyspace_name}' creada (o ya existe).")

        # Usar la keyspace recién creada
        session.set_keyspace(keyspace_name)
        print(f"Cambiando a la keyspace '{keyspace_name}'.")

        # 2. Crear tablas
        # Ejemplo de tabla: usuarios
        create_users_table_query = f"""
        CREATE TABLE IF NOT EXISTS {keyspace_name}.users (
            usuario_id UUID PRIMARY KEY,
            nombre TEXT,
            ciudad TEXT,
        );
        """
        session.execute(create_users_table_query)
        print(f"Tabla '{keyspace_name}.usuarios' creada (o ya existe).")

        # Crea Tabla Canciones
        create_song_table_query = f"""
        CREATE TABLE IF NOT EXISTS {keyspace_name}.song (
        cacion_id UUID PRIMARY KEY,
        artista TEXT,
        genero TEXT,
        titulo TEXT,
        anho int,
        );
        
        """
        session.execute(create_song_table_query)
        print(f"Tabla '{keyspace_name}.song' creada (o ya existe).")

        # Crear tabla Escuchas_por_usuario
        create_listen_song_by_user_table_query = f"""
        CREATE TABLE IF NOT EXISTS {keyspace_name}.listen_song_by_user (
            usuario_id UUID,
            cacion_id UUID,
            fecha_escucha timestamp,
            PRIMARY KEY ((usuario_id), fecha_escucha, cacion_id)
        ) WITH CLUSTERING ORDER BY (fecha_escucha DESC);
        """
        session.execute(create_listen_song_by_user_table_query)
        print(f"Tabla '{keyspace_name}.listen_song_by_user' Creada (o ya existe).")


        #crea tabla Escuhas por genero y mes [OLAP]
        create_listen_genero_mes = f"""
        CREATE TABLE IF NOT EXISTS {keyspace_name}.escuchas_por_genero_y_mes (
        genero text,
        anio int,
        mes int,
        total_escuchas counter,
        PRIMARY KEY ((genero, anio, mes))
        );
        """
        session.execute(create_listen_genero_mes)
        print(f"tabla genero_mes creada correcta")
        
        #CANCIONES ESCUCHADAS POR MES [OLAP]
        create_canciones_escuchadas_por_mes = f"""
        CREATE TABLE IF NOT EXISTS {keyspace_name}.canciones_escuchadas_por_mes (
        id_cancion UUID,
        anho int,
        mes int,
        total_escuchadas int,
        PRIMARY KEY ((id_cancion, anho, mes))
        );
        """

        # NUEVA TABLA: recomendaciones (para OLAP y recomendaciones)
        create_recommendations_table_query = f"""
        CREATE TABLE IF NOT EXISTS {keyspace_name}.recomendaciones(
            genero TEXT,
            cancion_id UUID,
            titulo TEXT,
            artista TEXT,
            total_escuchas COUNTER,
            PRIMARY KEY ((genero), total_escuchas DESC, cancion_id)
        );
        """
        session.execute(create_recommendations_table_query)
        print(f"Tabla '{keyspace_name}.recomendaciones' creada correctamente.")

        
        session.execute(create_canciones_escuchadas_por_mes)
        print(f"tabla genero_mes creada correcta")

        print("Esquema de Cassandra creado exitosamente.")

    except Exception as e:
        print(f"Error al crear el esquema de Cassandra: {e}")
    finally:
        if session:
            session.shutdown()
        if cluster:
            cluster.shutdown()
        print("Conexión a Cassandra cerrada.")

if __name__ == "__main__":
    # Puedes ajustar estos parámetros según tu configuración de Cassandra
    CASSANDRA_CONTACT_POINTS = ['127.0.0.1'] # Por defecto, es localhost
    CASSANDRA_PORT = 9042
    KEYSPACE_NAME = 'app_music'
    REPLICATION_FACTOR = 1 # Para un clúster de desarrollo de un solo nodo, 1 es suficiente.

    create_cassandra_schema_no_auth(
        contact_points=CASSANDRA_CONTACT_POINTS,
        port=CASSANDRA_PORT,
        keyspace_name=KEYSPACE_NAME,
        replication_factor=REPLICATION_FACTOR
    )
