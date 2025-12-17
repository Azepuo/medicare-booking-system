from flask import Flask

# Blueprints "pages"
from app.routes.medcin.medecin_routes import medecin

# Blueprints RPC
from app.rpc_medecin.disponibilites_rpc import disponibilites_rpc

# Routes disponibilités (normal)
<<<<<<< HEAD:app/app.py
from app.routes.routes_disponibilites import dispo
from app.rpc_medecin.patients_rpc import patients_rpc
=======
from app.routes.medcin.routes_disponibilites import dispo
>>>>>>> 6c2dca7c2628f3fc9bc2215a8b8d61b7666885da:app/main_medecin.py


def create_app():
    app = Flask(__name__)
    app.secret_key = "SECRET_KEY"

    # ========== Enregistrement des blueprints ==========
    app.register_blueprint(medecin, url_prefix="/medecin")

    # Blueprint RPC (pas de prefix : c’est direct /rpc/…)
    app.register_blueprint(disponibilites_rpc)

    # Blueprint des Disponibilités normales
    app.register_blueprint(dispo, url_prefix="/medecin")

    # Importez le blueprint RP

# Enregistrez-le
    app.register_blueprint(patients_rpc)

    # Route d'accueil
    @app.route('/')
    def index():
        return "<h1>Accueil OK</h1>"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True,port=5001)  # Port 5001 pour éviter conflit avec d'autres services
