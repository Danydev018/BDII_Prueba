
# Pasos Pa' desplaga esta vaina

Obviamente tener python, pip y Cassandara , previamente instalados.
## Instalar Pip (Gestor de paquetes de python)
Debian 12 :
```bash
  sudo apt install python3-pip
```
## Crear entorno virtual (Python)

Crear una carpeta en donde vas a clonar el repositorio

```bash
  mkdir App_music
  cd App_music
```
Una vez dentro de la carpeta, crear el entorno virtual de python.
## Linux
```bash
  python3 -m venv venv
```
Ahora clona el proyecto
```bash
  git clone https://github.com/cockr04ch/BDII_Prueba 
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