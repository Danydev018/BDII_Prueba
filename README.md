
# Pasos Pa' desplaga esta vaina

Obviamente tener python, pip y Cassandara , previamente instalados.
## Instalar Pip (Gestor de paquetes de python)
Debian 12 :
```bash
  sudo apt install python3-pip
```
## Crear entorno virtual (Python) y Crear la DB

 Clonar el repositorio

```bash
  git clone https://github.com/cockr04ch/BDII_Prueba 
  cd BDII_Prueba
```
## crear la DB con su respectiva keyspace
El script que les deje creara automaticamente la keyspace y las tablas : 
*OJO , ya Cassandra debe estar corriendo(activo)
```bash
python database.py
```

Una vez dentro de la carpeta, crear el entorno virtual de python.
## Linux
```bash
  python3 -m venv venv
```
Activar el entorno de python
```bash
  source venv/bin/activate
```
Bajar Dependencias del proyecto!
```bash
  pip install -r requirements.txt 
```
Una vez descargadas las dependencias, lanzar el proyecto : 
```bash
   python app/app.py
 ```

 ## Importar Datos a la DB mediante los CSV
 
 La carpeta csv contiene datos para insertar en la tablas, tienen que hacerlo directemente de Cassandra(cqlsh)

```bash
cqlsh
```

usar la Keyspace antes creada

```bash
USE app_music ;
```

Comando para insertar datos, dentro de las comillas poner la ruta en la que se encuntra el csv , OJO no pongan los <> :
ejemplo con song : 

```bash
COPY song (cacion_id , titulo , artista , genero ) FROM '/home/daniel/DBII_Prueba/csv/song.csv' WITH HEADER = true ;
COPY users (user_id , ciudad , nombre ) FROM '/home/daniel/DBII_Prueba/csv/users.csv' WITH HEADER = true ;
```
## Habilitar Busqueda

```bash
cqlsh
```
usar la Keyspace antes creada

```bash
USE app_music ;
```

Comando para habilitar la busqueda por titulo de las canciones
```bash
CREATE CUSTOM INDEX IF NOT EXISTS song_titulo_sasi ON song (titulo) USING 'org.apache.cassandra.index.sasi.SASIIndex' WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer', 'case_sensitive': 'false'};
```
