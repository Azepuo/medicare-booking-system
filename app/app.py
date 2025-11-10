from flask import Flask, render_template

# Import des Blueprints
from app.routes.auth_routes import auth
from app.routes.patient_routes import patient

app = Flask(__name__)

# Route d'accueil
@app.route('/')
def index():
 return render_template('index.html')

# Enregistrement des Blueprints
app.register_blueprint(auth)
app.register_blueprint(patient)

if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    app.run(debug=True)
