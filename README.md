# <h1 align="center" >🎵 🎶 RITMO PURO 🎶 🎵</h1>

<p align="center">
  <img src="repository/index.gif" width="100%">
</p>

<p align="center">
  <strong>✨ Descubre tu próxima obsesión musical ✨</strong>
</p>

---

## 🚀 Sobre el Proyecto

**RITMO PURO** es una aplicación web diseñada para amantes de la música que buscan descubrir nuevos artistas y canciones. Nuestra plataforma te permite explorar un vasto universo musical, ver recomendaciones personalizadas y conectar con una comunidad de apasionados por el ritmo.

## 🛠️ Tecnologías Utilizadas

Este proyecto ha sido construido utilizando las siguientes tecnologías:

<p align="center">
  <a href="https://www.python.org/" target="_blank">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://pip.pypa.io/en/stable/" target="_blank">
    <img src="https://img.shields.io/badge/Pip-3776AB?style=for-the-badge&logo=pypi&logoColor=white" alt="Pip">
  </a>
  <a href="https://cassandra.apache.org/" target="_blank">
    <img src="https://img.shields.io/badge/Cassandra-1287B1?style=for-the-badge&logo=apache-cassandra&logoColor=white" alt="Cassandra">
  </a>
</p>

## ✅ Requisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu entorno de desarrollo:

* **Python:** `python>=3.11`
* **Pip:** `(manejador de paquetes para Python)`
* **Apache Cassandra:** `(Base de Datos NoSQL)`

## 🏁 Cómo Empezar

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### 1. Clona el Repositorio

```bash
  git clone https://github.com/cockr04ch/BDII_Prueba
  cd BDII_Prueba
```

### 2. Crea un Entorno Virtual

Es una buena práctica trabajar dentro de un entorno virtual.

```bash
# Para Windows
python -m venv venv
venv\Scripts\activate

# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instala las Dependencias

Utiliza `pip` para instalar todas las librerías necesarias que se encuentran en el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

*(Nota: Asegúrate de estar en el directorio raiz , estara un archivo `requirements.txt` necesario para la instalacion de las librerias.)*

### 4. Configura la Base de Datos

Asegúrate de que tu instancia de Cassandra esté en funcionamiento. Deberás configurar la conexión en el archivo de configuración del proyecto.
Para Facilitar la creacion de las Keyspace y tablas pruebe a ejecutar el script database.py
```bash
python database.py
```

*(Este Script configurara la conexión a Cassandra, como la creación del keyspace, tablas, etc.)*

### 5. Ejecuta la Aplicación

```bash
python app/app.py
```

¡Y listo! Abre tu navegador y visita `http://127.0.0.1:5000` (o el puerto que hayas configurado).

---


<p align="center">
  Hecho con ❤️ por [ Canchis Victor | Rojas Tairon | Nuñez Daniel ]
</p>
