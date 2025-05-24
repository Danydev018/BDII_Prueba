# app.py
from flask import Flask
from routes import main_bp

app = Flask(__name__)

# Blueprint (Esta vaina e' para exportar las rutas)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
